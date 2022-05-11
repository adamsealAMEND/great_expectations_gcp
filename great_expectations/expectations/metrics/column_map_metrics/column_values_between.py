
import warnings
from dateutil.parser import parse
from great_expectations.execution_engine import PandasExecutionEngine, SparkDFExecutionEngine, SqlAlchemyExecutionEngine
from great_expectations.expectations.metrics.import_manager import sa
from great_expectations.expectations.metrics.map_metric_provider import ColumnMapMetricProvider, column_condition_partial

class ColumnValuesBetween(ColumnMapMetricProvider):
    condition_metric_name = 'column_values.between'
    condition_value_keys = ('min_value', 'max_value', 'strict_min', 'strict_max', 'parse_strings_as_datetimes', 'allow_cross_type_comparisons')

    @column_condition_partial(engine=PandasExecutionEngine)
    def _pandas(cls, column, min_value=None, max_value=None, strict_min=None, strict_max=None, parse_strings_as_datetimes: bool=False, allow_cross_type_comparisons=None, **kwargs):
        import inspect
        __frame = inspect.currentframe()
        __file = __frame.f_code.co_filename
        __func = __frame.f_code.co_name
        for (k, v) in __frame.f_locals.items():
            if any(((var in k) for var in ('self', 'cls', '__frame', '__file', '__func'))):
                continue
            print(f'<INTROSPECT> {__file}:{__func}:{k} - {v.__class__.__name__}')
        if ((min_value is None) and (max_value is None)):
            raise ValueError('min_value and max_value cannot both be None')
        if parse_strings_as_datetimes:
            warnings.warn('The parameter "parse_strings_as_datetimes" is deprecated as of v0.13.41 in v0.16. As part of the V3 API transition, we\'ve moved away from input transformation. For more information, please see: https://greatexpectations.io/blog/why_we_dont_do_transformations_for_expectations/\n', DeprecationWarning)
            if (min_value is not None):
                try:
                    min_value = parse(min_value)
                except TypeError:
                    pass
            if (max_value is not None):
                try:
                    max_value = parse(max_value)
                except TypeError:
                    pass
            try:
                temp_column = column.map(parse)
            except TypeError:
                temp_column = column
        else:
            temp_column = column
        if ((min_value is not None) and (max_value is not None) and (min_value > max_value)):
            raise ValueError('min_value cannot be greater than max_value')

        def is_between(val):
            import inspect
            __frame = inspect.currentframe()
            __file = __frame.f_code.co_filename
            __func = __frame.f_code.co_name
            for (k, v) in __frame.f_locals.items():
                if any(((var in k) for var in ('self', 'cls', '__frame', '__file', '__func'))):
                    continue
                print(f'<INTROSPECT> {__file}:{__func}:{k} - {v.__class__.__name__}')
            if (type(val) is None):
                return False
            if ((min_value is not None) and (max_value is not None)):
                if allow_cross_type_comparisons:
                    try:
                        if (strict_min and strict_max):
                            return ((min_value < val) and (val < max_value))
                        elif strict_min:
                            return ((min_value < val) and (val <= max_value))
                        elif strict_max:
                            return ((min_value <= val) and (val < max_value))
                        else:
                            return ((min_value <= val) and (val <= max_value))
                    except TypeError:
                        return False
                else:
                    if ((isinstance(val, str) != isinstance(min_value, str)) or (isinstance(val, str) != isinstance(max_value, str))):
                        raise TypeError('Column values, min_value, and max_value must either be None or of the same type.')
                    if (strict_min and strict_max):
                        return ((min_value < val) and (val < max_value))
                    elif strict_min:
                        return ((min_value < val) and (val <= max_value))
                    elif strict_max:
                        return ((min_value <= val) and (val < max_value))
                    else:
                        return ((min_value <= val) and (val <= max_value))
            elif ((min_value is None) and (max_value is not None)):
                if allow_cross_type_comparisons:
                    try:
                        if strict_max:
                            return (val < max_value)
                        else:
                            return (val <= max_value)
                    except TypeError:
                        return False
                else:
                    if (isinstance(val, str) != isinstance(max_value, str)):
                        raise TypeError('Column values, min_value, and max_value must either be None or of the same type.')
                    if strict_max:
                        return (val < max_value)
                    else:
                        return (val <= max_value)
            elif ((min_value is not None) and (max_value is None)):
                if allow_cross_type_comparisons:
                    try:
                        if strict_min:
                            return (min_value < val)
                        else:
                            return (min_value <= val)
                    except TypeError:
                        return False
                else:
                    if (isinstance(val, str) != isinstance(min_value, str)):
                        raise TypeError('Column values, min_value, and max_value must either be None or of the same type.')
                    if strict_min:
                        return (min_value < val)
                    else:
                        return (min_value <= val)
            else:
                return False
        return temp_column.map(is_between)

    @column_condition_partial(engine=SqlAlchemyExecutionEngine)
    def _sqlalchemy(cls, column, min_value=None, max_value=None, strict_min=None, strict_max=None, parse_strings_as_datetimes: bool=False, **kwargs):
        import inspect
        __frame = inspect.currentframe()
        __file = __frame.f_code.co_filename
        __func = __frame.f_code.co_name
        for (k, v) in __frame.f_locals.items():
            if any(((var in k) for var in ('self', 'cls', '__frame', '__file', '__func'))):
                continue
            print(f'<INTROSPECT> {__file}:{__func}:{k} - {v.__class__.__name__}')
        if parse_strings_as_datetimes:
            warnings.warn('The parameter "parse_strings_as_datetimes" is deprecated as of v0.13.41 in v0.16. As part of the V3 API transition, we\'ve moved away from input transformation. For more information, please see: https://greatexpectations.io/blog/why_we_dont_do_transformations_for_expectations/\n', DeprecationWarning)
            if (min_value is not None):
                try:
                    min_value = parse(min_value)
                except TypeError:
                    pass
            if (max_value is not None):
                try:
                    max_value = parse(max_value)
                except TypeError:
                    pass
        if ((min_value is not None) and (max_value is not None) and (min_value > max_value)):
            raise ValueError('min_value cannot be greater than max_value')
        if ((min_value is None) and (max_value is None)):
            raise ValueError('min_value and max_value cannot both be None')
        if (min_value is None):
            if strict_max:
                return (column < max_value)
            else:
                return (column <= max_value)
        elif (max_value is None):
            if strict_min:
                return (min_value < column)
            else:
                return (min_value <= column)
        elif (strict_min and strict_max):
            return sa.and_((min_value < column), (column < max_value))
        elif strict_min:
            return sa.and_((min_value < column), (column <= max_value))
        elif strict_max:
            return sa.and_((min_value <= column), (column < max_value))
        else:
            return sa.and_((min_value <= column), (column <= max_value))

    @column_condition_partial(engine=SparkDFExecutionEngine)
    def _spark(cls, column, min_value=None, max_value=None, strict_min=None, strict_max=None, parse_strings_as_datetimes: bool=False, **kwargs):
        import inspect
        __frame = inspect.currentframe()
        __file = __frame.f_code.co_filename
        __func = __frame.f_code.co_name
        for (k, v) in __frame.f_locals.items():
            if any(((var in k) for var in ('self', 'cls', '__frame', '__file', '__func'))):
                continue
            print(f'<INTROSPECT> {__file}:{__func}:{k} - {v.__class__.__name__}')
        if parse_strings_as_datetimes:
            warnings.warn('The parameter "parse_strings_as_datetimes" is deprecated as of v0.13.41 in v0.16. As part of the V3 API transition, we\'ve moved away from input transformation. For more information, please see: https://greatexpectations.io/blog/why_we_dont_do_transformations_for_expectations/\n', DeprecationWarning)
            if (min_value is not None):
                try:
                    min_value = parse(min_value)
                except TypeError:
                    pass
            if (max_value is not None):
                try:
                    max_value = parse(max_value)
                except TypeError:
                    pass
        if ((min_value is not None) and (max_value is not None) and (min_value > max_value)):
            raise ValueError('min_value cannot be greater than max_value')
        if ((min_value is None) and (max_value is None)):
            raise ValueError('min_value and max_value cannot both be None')
        if (min_value is None):
            if strict_max:
                return (column < max_value)
            else:
                return (column <= max_value)
        elif (max_value is None):
            if strict_min:
                return (min_value < column)
            else:
                return (min_value <= column)
        elif (strict_min and strict_max):
            return ((min_value < column) & (column < max_value))
        elif strict_min:
            return ((min_value < column) & (column <= max_value))
        elif strict_max:
            return ((min_value <= column) & (column < max_value))
        else:
            return ((min_value <= column) & (column <= max_value))
