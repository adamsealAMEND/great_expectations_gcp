
import itertools
import logging
import traceback
from collections.abc import Iterable
from typing import Any, Dict, List
import numpy as np
from great_expectations.execution_engine import PandasExecutionEngine, SparkDFExecutionEngine, SqlAlchemyExecutionEngine
from great_expectations.execution_engine.execution_engine import MetricDomainTypes
from great_expectations.execution_engine.util import get_approximate_percentile_disc_sql
from great_expectations.expectations.metrics.column_aggregate_metric_provider import ColumnAggregateMetricProvider, column_aggregate_value
from great_expectations.expectations.metrics.import_manager import sa
from great_expectations.expectations.metrics.metric_provider import metric_value
from great_expectations.expectations.metrics.util import attempt_allowing_relative_error
logger = logging.getLogger(__name__)
try:
    from sqlalchemy.exc import ProgrammingError
    from sqlalchemy.sql import Select
    from sqlalchemy.sql.elements import Label, TextClause, WithinGroup
    from sqlalchemy.sql.selectable import CTE
except ImportError:
    logger.debug('Unable to load SqlAlchemy context; install optional sqlalchemy dependency for support')
    ProgrammingError = None
    Select = None
    Label = None
    TextClause = None
    WithinGroup = None
    CTE = None
try:
    from sqlalchemy.engine.row import Row
except ImportError:
    try:
        from sqlalchemy.engine.row import RowProxy
        Row = RowProxy
    except ImportError:
        logger.debug('Unable to load SqlAlchemy Row class; please upgrade you sqlalchemy installation to the latest version.')
        RowProxy = None
        Row = None

class ColumnQuantileValues(ColumnAggregateMetricProvider):
    metric_name = 'column.quantile_values'
    value_keys = ('quantiles', 'allow_relative_error')

    @column_aggregate_value(engine=PandasExecutionEngine)
    def _pandas(cls, column, quantiles, allow_relative_error, **kwargs):
        import inspect
        __frame = inspect.currentframe()
        __file = __frame.f_code.co_filename
        __func = __frame.f_code.co_name
        for (k, v) in __frame.f_locals.items():
            if any(((var in k) for var in ('self', 'cls', '__frame', '__file', '__func'))):
                continue
            print(f'<INTROSPECT> {__file}:{__func}:{k} - {v.__class__.__name__}')
        'Quantile Function'
        interpolation_options = ('linear', 'lower', 'higher', 'midpoint', 'nearest')
        if (not allow_relative_error):
            allow_relative_error = 'nearest'
        if (allow_relative_error not in interpolation_options):
            raise ValueError(f"If specified for pandas, allow_relative_error must be one an allowed value for the 'interpolation'parameter of .quantile() (one of {interpolation_options})")
        return column.quantile(quantiles, interpolation=allow_relative_error).tolist()

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
        (selectable, compute_domain_kwargs, accessor_domain_kwargs) = execution_engine.get_compute_domain(metric_domain_kwargs, domain_type=MetricDomainTypes.COLUMN)
        column_name = accessor_domain_kwargs['column']
        column = sa.column(column_name)
        sqlalchemy_engine = execution_engine.engine
        dialect = sqlalchemy_engine.dialect
        quantiles = metric_value_kwargs['quantiles']
        allow_relative_error = metric_value_kwargs.get('allow_relative_error', False)
        table_row_count = metrics.get('table.row_count')
        if (dialect.name.lower() == 'mssql'):
            return _get_column_quantiles_mssql(column=column, quantiles=quantiles, selectable=selectable, sqlalchemy_engine=sqlalchemy_engine)
        elif (dialect.name.lower() == 'bigquery'):
            return _get_column_quantiles_bigquery(column=column, quantiles=quantiles, selectable=selectable, sqlalchemy_engine=sqlalchemy_engine)
        elif (dialect.name.lower() == 'mysql'):
            return _get_column_quantiles_mysql(column=column, quantiles=quantiles, selectable=selectable, sqlalchemy_engine=sqlalchemy_engine)
        elif (dialect.name.lower() == 'snowflake'):
            quantiles = [round(x, 10) for x in quantiles]
            return _get_column_quantiles_generic_sqlalchemy(column=column, quantiles=quantiles, allow_relative_error=allow_relative_error, dialect=dialect, selectable=selectable, sqlalchemy_engine=sqlalchemy_engine)
        elif (dialect.name.lower() == 'sqlite'):
            return _get_column_quantiles_sqlite(column=column, quantiles=quantiles, selectable=selectable, sqlalchemy_engine=sqlalchemy_engine, table_row_count=table_row_count)
        else:
            return _get_column_quantiles_generic_sqlalchemy(column=column, quantiles=quantiles, allow_relative_error=allow_relative_error, dialect=dialect, selectable=selectable, sqlalchemy_engine=sqlalchemy_engine)

    @metric_value(engine=SparkDFExecutionEngine)
    def _spark(cls, execution_engine: SqlAlchemyExecutionEngine, metric_domain_kwargs: Dict, metric_value_kwargs: Dict, metrics: Dict[(str, Any)], runtime_configuration: Dict):
        import inspect
        __frame = inspect.currentframe()
        __file = __frame.f_code.co_filename
        __func = __frame.f_code.co_name
        for (k, v) in __frame.f_locals.items():
            if any(((var in k) for var in ('self', 'cls', '__frame', '__file', '__func'))):
                continue
            print(f'<INTROSPECT> {__file}:{__func}:{k} - {v.__class__.__name__}')
        (df, compute_domain_kwargs, accessor_domain_kwargs) = execution_engine.get_compute_domain(metric_domain_kwargs, domain_type=MetricDomainTypes.COLUMN)
        allow_relative_error = metric_value_kwargs.get('allow_relative_error', False)
        quantiles = metric_value_kwargs['quantiles']
        column = accessor_domain_kwargs['column']
        if (allow_relative_error is False):
            allow_relative_error = 0.0
        if ((not isinstance(allow_relative_error, float)) or (allow_relative_error < 0) or (allow_relative_error > 1)):
            raise ValueError('SparkDFDataset requires relative error to be False or to be a float between 0 and 1.')
        return df.approxQuantile(column, list(quantiles), allow_relative_error)

def _get_column_quantiles_mssql(column, quantiles: Iterable, selectable, sqlalchemy_engine) -> list:
    import inspect
    __frame = inspect.currentframe()
    __file = __frame.f_code.co_filename
    __func = __frame.f_code.co_name
    for (k, v) in __frame.f_locals.items():
        if any(((var in k) for var in ('self', 'cls', '__frame', '__file', '__func'))):
            continue
        print(f'<INTROSPECT> {__file}:{__func}:{k} - {v.__class__.__name__}')
    selects: List[WithinGroup] = [sa.func.percentile_disc(quantile).within_group(column.asc()).over() for quantile in quantiles]
    quantiles_query: Select = sa.select(selects).select_from(selectable)
    try:
        quantiles_results: Row = sqlalchemy_engine.execute(quantiles_query).fetchone()
        return list(quantiles_results)
    except ProgrammingError as pe:
        exception_message: str = 'An SQL syntax Exception occurred.'
        exception_traceback: str = traceback.format_exc()
        exception_message += f'{type(pe).__name__}: "{str(pe)}".  Traceback: "{exception_traceback}".'
        logger.error(exception_message)
        raise pe

def _get_column_quantiles_bigquery(column, quantiles: Iterable, selectable, sqlalchemy_engine) -> list:
    import inspect
    __frame = inspect.currentframe()
    __file = __frame.f_code.co_filename
    __func = __frame.f_code.co_name
    for (k, v) in __frame.f_locals.items():
        if any(((var in k) for var in ('self', 'cls', '__frame', '__file', '__func'))):
            continue
        print(f'<INTROSPECT> {__file}:{__func}:{k} - {v.__class__.__name__}')
    selects: List[WithinGroup] = [sa.func.percentile_disc(column, quantile).over() for quantile in quantiles]
    quantiles_query: Select = sa.select(selects).select_from(selectable)
    try:
        quantiles_results: Row = sqlalchemy_engine.execute(quantiles_query).fetchone()
        return list(quantiles_results)
    except ProgrammingError as pe:
        exception_message: str = 'An SQL syntax Exception occurred.'
        exception_traceback: str = traceback.format_exc()
        exception_message += f'{type(pe).__name__}: "{str(pe)}".  Traceback: "{exception_traceback}".'
        logger.error(exception_message)
        raise pe

def _get_column_quantiles_mysql(column, quantiles: Iterable, selectable, sqlalchemy_engine) -> list:
    import inspect
    __frame = inspect.currentframe()
    __file = __frame.f_code.co_filename
    __func = __frame.f_code.co_name
    for (k, v) in __frame.f_locals.items():
        if any(((var in k) for var in ('self', 'cls', '__frame', '__file', '__func'))):
            continue
        print(f'<INTROSPECT> {__file}:{__func}:{k} - {v.__class__.__name__}')
    percent_rank_query: CTE = sa.select([column, sa.cast(sa.func.percent_rank().over(order_by=column.asc()), sa.dialects.mysql.DECIMAL(18, 15)).label('p')]).order_by(sa.column('p').asc()).select_from(selectable).cte('t')
    selects: List[WithinGroup] = []
    for (idx, quantile) in enumerate(quantiles):
        if np.issubdtype(type(quantile), np.float_):
            quantile = float(quantile)
        quantile_column: Label = sa.func.first_value(column).over(order_by=sa.case([((percent_rank_query.c.p <= sa.cast(quantile, sa.dialects.mysql.DECIMAL(18, 15))), percent_rank_query.c.p)], else_=None).desc()).label(f'q_{idx}')
        selects.append(quantile_column)
    quantiles_query: Select = sa.select(selects).distinct().order_by(percent_rank_query.c.p.desc())
    try:
        quantiles_results: Row = sqlalchemy_engine.execute(quantiles_query).fetchone()
        return list(quantiles_results)
    except ProgrammingError as pe:
        exception_message: str = 'An SQL syntax Exception occurred.'
        exception_traceback: str = traceback.format_exc()
        exception_message += f'{type(pe).__name__}: "{str(pe)}".  Traceback: "{exception_traceback}".'
        logger.error(exception_message)
        raise pe

def _get_column_quantiles_sqlite(column, quantiles: Iterable, selectable, sqlalchemy_engine, table_row_count) -> list:
    import inspect
    __frame = inspect.currentframe()
    __file = __frame.f_code.co_filename
    __func = __frame.f_code.co_name
    for (k, v) in __frame.f_locals.items():
        if any(((var in k) for var in ('self', 'cls', '__frame', '__file', '__func'))):
            continue
        print(f'<INTROSPECT> {__file}:{__func}:{k} - {v.__class__.__name__}')
    '\n    The present implementation is somewhat inefficient, because it requires as many calls to\n    "sqlalchemy_engine.execute()" as the number of partitions in the "quantiles" parameter (albeit, typically,\n    only a few).  However, this is the only mechanism available for SQLite at the present time (11/17/2021), because\n    the analytical processing is not a very strongly represented capability of the SQLite database management system.\n    '
    offsets: List[int] = [((quantile * table_row_count) - 1) for quantile in quantiles]
    quantile_queries: List[Select] = [sa.select([column]).order_by(column.asc()).offset(offset).limit(1).select_from(selectable) for offset in offsets]
    quantile_result: Row
    quantile_query: Select
    try:
        quantiles_results: List[Row] = [sqlalchemy_engine.execute(quantile_query).fetchone() for quantile_query in quantile_queries]
        return list(itertools.chain.from_iterable([list(quantile_result) for quantile_result in quantiles_results]))
    except ProgrammingError as pe:
        exception_message: str = 'An SQL syntax Exception occurred.'
        exception_traceback: str = traceback.format_exc()
        exception_message += f'{type(pe).__name__}: "{str(pe)}".  Traceback: "{exception_traceback}".'
        logger.error(exception_message)
        raise pe

def _get_column_quantiles_generic_sqlalchemy(column, quantiles: Iterable, allow_relative_error: bool, dialect, selectable, sqlalchemy_engine) -> list:
    import inspect
    __frame = inspect.currentframe()
    __file = __frame.f_code.co_filename
    __func = __frame.f_code.co_name
    for (k, v) in __frame.f_locals.items():
        if any(((var in k) for var in ('self', 'cls', '__frame', '__file', '__func'))):
            continue
        print(f'<INTROSPECT> {__file}:{__func}:{k} - {v.__class__.__name__}')
    selects: List[WithinGroup] = [sa.func.percentile_disc(quantile).within_group(column.asc()) for quantile in quantiles]
    quantiles_query: Select = sa.select(selects).select_from(selectable)
    try:
        quantiles_results: Row = sqlalchemy_engine.execute(quantiles_query).fetchone()
        return list(quantiles_results)
    except ProgrammingError:
        if attempt_allowing_relative_error(dialect):
            sql_approx: str = get_approximate_percentile_disc_sql(selects=selects, sql_engine_dialect=dialect)
            selects_approx: List[TextClause] = [sa.text(sql_approx)]
            quantiles_query_approx: Select = sa.select(selects_approx).select_from(selectable)
            if allow_relative_error:
                try:
                    quantiles_results: Row = sqlalchemy_engine.execute(quantiles_query_approx).fetchone()
                    return list(quantiles_results)
                except ProgrammingError as pe:
                    exception_message: str = 'An SQL syntax Exception occurred.'
                    exception_traceback: str = traceback.format_exc()
                    exception_message += f'{type(pe).__name__}: "{str(pe)}".  Traceback: "{exception_traceback}".'
                    logger.error(exception_message)
                    raise pe
            else:
                raise ValueError(f'The SQL engine dialect "{str(dialect)}" does not support computing quantiles without approximation error; set allow_relative_error to True to allow approximate quantiles.')
        else:
            raise ValueError(f'The SQL engine dialect "{str(dialect)}" does not support computing quantiles with approximation error; set allow_relative_error to False to disable approximate quantiles.')
