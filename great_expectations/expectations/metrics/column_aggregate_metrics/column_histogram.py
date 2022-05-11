
import copy
import logging
from typing import Any, Dict
import numpy as np
from great_expectations.core.util import convert_to_json_serializable, get_sql_dialect_floating_point_infinity_value
from great_expectations.execution_engine import PandasExecutionEngine, SparkDFExecutionEngine, SqlAlchemyExecutionEngine
from great_expectations.execution_engine.execution_engine import MetricDomainTypes
from great_expectations.expectations.metrics.column_aggregate_metric_provider import ColumnAggregateMetricProvider
from great_expectations.expectations.metrics.import_manager import Bucketizer, F, sa
from great_expectations.expectations.metrics.metric_provider import metric_value
logger = logging.getLogger(__name__)

class ColumnHistogram(ColumnAggregateMetricProvider):
    metric_name = 'column.histogram'
    value_keys = ('bins',)

    @metric_value(engine=PandasExecutionEngine)
    def _pandas(cls, execution_engine: PandasExecutionEngine, metric_domain_kwargs: Dict, metric_value_kwargs: Dict, metrics: Dict[(str, Any)], runtime_configuration: Dict):
        import inspect
        __frame = inspect.currentframe()
        __file = __frame.f_code.co_filename
        __func = __frame.f_code.co_name
        for (k, v) in __frame.f_locals.items():
            if any(((var in k) for var in ('self', 'cls', '__frame', '__file', '__func'))):
                continue
            print(f'<INTROSPECT> {__file}:{__func}:{k} - {v.__class__.__name__}')
        (df, _, accessor_domain_kwargs) = execution_engine.get_compute_domain(domain_kwargs=metric_domain_kwargs, domain_type=MetricDomainTypes.COLUMN)
        column = accessor_domain_kwargs['column']
        bins = metric_value_kwargs['bins']
        (hist, bin_edges) = np.histogram(df[column], bins, density=False)
        return list(hist)

    @metric_value(engine=SqlAlchemyExecutionEngine)
    def _sqlalchemy(cls, execution_engine: SqlAlchemyExecutionEngine, metric_domain_kwargs: Dict, metric_value_kwargs: Dict, metrics: Dict[(str, Any)], runtime_configuration: Dict):
        import inspect
        __frame = inspect.currentframe()
        __file = __frame.f_code.co_filename
        __func = __frame.f_code.co_name
        for (k, v) in __frame.f_locals.items():
            if any(((var in k) for var in ('self', 'cls', '__frame', '__file', '__func'))):
                continue
            print(f'<INTROSPECT> {__file}:{__func}:{k} - {v.__class__.__name__}')
        'return a list of counts corresponding to bins\n\n        Args:\n            column: the name of the column for which to get the histogram\n            bins: tuple of bin edges for which to get histogram values; *must* be tuple to support caching\n        '
        (selectable, _, accessor_domain_kwargs) = execution_engine.get_compute_domain(domain_kwargs=metric_domain_kwargs, domain_type=MetricDomainTypes.COLUMN)
        column = accessor_domain_kwargs['column']
        bins = metric_value_kwargs['bins']
        case_conditions = []
        idx = 0
        if isinstance(bins, np.ndarray):
            bins = bins.tolist()
        else:
            bins = list(bins)
        if ((bins[0] == get_sql_dialect_floating_point_infinity_value(schema='api_np', negative=True)) or (bins[0] == get_sql_dialect_floating_point_infinity_value(schema='api_cast', negative=True))):
            case_conditions.append(sa.func.sum(sa.case([((sa.column(column) < bins[(idx + 1)]), 1)], else_=0)).label(f'bin_{str(idx)}'))
            idx += 1
        for idx in range(idx, (len(bins) - 2)):
            case_conditions.append(sa.func.sum(sa.case([(sa.and_((bins[idx] <= sa.column(column)), (sa.column(column) < bins[(idx + 1)])), 1)], else_=0)).label(f'bin_{str(idx)}'))
        if ((bins[(- 1)] == get_sql_dialect_floating_point_infinity_value(schema='api_np', negative=False)) or (bins[(- 1)] == get_sql_dialect_floating_point_infinity_value(schema='api_cast', negative=False))):
            case_conditions.append(sa.func.sum(sa.case([((bins[(- 2)] <= sa.column(column)), 1)], else_=0)).label(f'bin_{str((len(bins) - 1))}'))
        else:
            case_conditions.append(sa.func.sum(sa.case([(sa.and_((bins[(- 2)] <= sa.column(column)), (sa.column(column) <= bins[(- 1)])), 1)], else_=0)).label(f'bin_{str((len(bins) - 1))}'))
        query = sa.select(case_conditions).where((sa.column(column) != None)).select_from(selectable)
        hist = convert_to_json_serializable(list(execution_engine.engine.execute(query).fetchone()))
        return hist

    @metric_value(engine=SparkDFExecutionEngine)
    def _spark(cls, execution_engine: SparkDFExecutionEngine, metric_domain_kwargs: Dict, metric_value_kwargs: Dict, metrics: Dict[(str, Any)], runtime_configuration: Dict):
        import inspect
        __frame = inspect.currentframe()
        __file = __frame.f_code.co_filename
        __func = __frame.f_code.co_name
        for (k, v) in __frame.f_locals.items():
            if any(((var in k) for var in ('self', 'cls', '__frame', '__file', '__func'))):
                continue
            print(f'<INTROSPECT> {__file}:{__func}:{k} - {v.__class__.__name__}')
        (df, _, accessor_domain_kwargs) = execution_engine.get_compute_domain(domain_kwargs=metric_domain_kwargs, domain_type=MetricDomainTypes.COLUMN)
        bins = metric_value_kwargs['bins']
        column = metric_domain_kwargs['column']
        'return a list of counts corresponding to bins'
        bins = list(copy.deepcopy(bins))
        if ((bins[0] == (- np.inf)) or (bins[0] == (- float('inf')))):
            added_min = False
            bins[0] = (- float('inf'))
        else:
            added_min = True
            bins.insert(0, (- float('inf')))
        if ((bins[(- 1)] == np.inf) or (bins[(- 1)] == float('inf'))):
            added_max = False
            bins[(- 1)] = float('inf')
        else:
            added_max = True
            bins.append(float('inf'))
        temp_column = df.select(column).where(F.col(column).isNotNull())
        bucketizer = Bucketizer(splits=bins, inputCol=column, outputCol='buckets')
        bucketed = bucketizer.setHandleInvalid('skip').transform(temp_column)
        if added_max:
            upper_bound_count = temp_column.select(column).filter((F.col(column) == bins[(- 2)])).count()
        else:
            upper_bound_count = 0
        hist_rows = bucketed.groupBy('buckets').count().collect()
        hist = ([0] * (len(bins) - 1))
        for row in hist_rows:
            hist[int(row['buckets'])] = row['count']
        hist[(- 2)] += upper_bound_count
        if added_min:
            below_bins = hist.pop(0)
            bins.pop(0)
            if (below_bins > 0):
                logger.warning('Discarding histogram values below lowest bin.')
        if added_max:
            above_bins = hist.pop((- 1))
            bins.pop((- 1))
            if (above_bins > 0):
                logger.warning('Discarding histogram values above highest bin.')
        return hist
