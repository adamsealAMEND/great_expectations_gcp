
import datetime
import json
import logging
from typing import Any, Callable, Dict, Optional, Set, Union
import great_expectations.exceptions as ge_exceptions
from great_expectations.core.id_dict import BatchKwargs, BatchSpec, IDDict
from great_expectations.core.util import convert_to_json_serializable
from great_expectations.exceptions import InvalidBatchIdError
from great_expectations.types import DictDot, SerializableDictDot, safe_deep_copy
from great_expectations.util import deep_filter_properties_iterable
from great_expectations.validator.metric_configuration import MetricConfiguration
logger = logging.getLogger(__name__)
try:
    import pyspark
except ImportError:
    pyspark = None
    logger.debug('Unable to load pyspark; install optional spark dependency if you will be working with Spark dataframes')

class BatchDefinition(SerializableDictDot):

    def __init__(self, datasource_name: str, data_connector_name: str, data_asset_name: str, batch_identifiers: IDDict, batch_spec_passthrough: Optional[dict]=None) -> None:
        import inspect
        __frame = inspect.currentframe()
        __file = __frame.f_code.co_filename
        __func = __frame.f_code.co_name
        for (k, v) in __frame.f_locals.items():
            if any(((var in k) for var in ('self', 'cls', '__frame', '__file', '__func'))):
                continue
            print(f'<INTROSPECT> {__file}:{__func}:{k} - {v.__class__.__name__}')
        self._validate_batch_definition(datasource_name=datasource_name, data_connector_name=data_connector_name, data_asset_name=data_asset_name, batch_identifiers=batch_identifiers)
        assert (type(batch_identifiers) == IDDict)
        self._datasource_name = datasource_name
        self._data_connector_name = data_connector_name
        self._data_asset_name = data_asset_name
        self._batch_identifiers = batch_identifiers
        self._batch_spec_passthrough = batch_spec_passthrough

    def to_json_dict(self) -> dict:
        import inspect
        __frame = inspect.currentframe()
        __file = __frame.f_code.co_filename
        __func = __frame.f_code.co_name
        for (k, v) in __frame.f_locals.items():
            if any(((var in k) for var in ('self', 'cls', '__frame', '__file', '__func'))):
                continue
            print(f'<INTROSPECT> {__file}:{__func}:{k} - {v.__class__.__name__}')
        return convert_to_json_serializable({'datasource_name': self.datasource_name, 'data_connector_name': self.data_connector_name, 'data_asset_name': self.data_asset_name, 'batch_identifiers': self.batch_identifiers})

    def __repr__(self) -> str:
        import inspect
        __frame = inspect.currentframe()
        __file = __frame.f_code.co_filename
        __func = __frame.f_code.co_name
        for (k, v) in __frame.f_locals.items():
            if any(((var in k) for var in ('self', 'cls', '__frame', '__file', '__func'))):
                continue
            print(f'<INTROSPECT> {__file}:{__func}:{k} - {v.__class__.__name__}')
        doc_fields_dict: dict = {'datasource_name': self._datasource_name, 'data_connector_name': self._data_connector_name, 'data_asset_name': self.data_asset_name, 'batch_identifiers': self._batch_identifiers}
        return str(doc_fields_dict)

    @staticmethod
    def _validate_batch_definition(datasource_name: str, data_connector_name: str, data_asset_name: str, batch_identifiers: IDDict) -> None:
        import inspect
        __frame = inspect.currentframe()
        __file = __frame.f_code.co_filename
        __func = __frame.f_code.co_name
        for (k, v) in __frame.f_locals.items():
            if any(((var in k) for var in ('self', 'cls', '__frame', '__file', '__func'))):
                continue
            print(f'<INTROSPECT> {__file}:{__func}:{k} - {v.__class__.__name__}')
        if (datasource_name is None):
            raise ValueError('A valid datasource must be specified.')
        if (datasource_name and (not isinstance(datasource_name, str))):
            raise TypeError(f'''The type of an datasource name must be a string (Python "str").  The type given is
"{str(type(datasource_name))}", which is illegal.
            ''')
        if (data_connector_name is None):
            raise ValueError('A valid data_connector must be specified.')
        if (data_connector_name and (not isinstance(data_connector_name, str))):
            raise TypeError(f'''The type of a data_connector name must be a string (Python "str").  The type given is
"{str(type(data_connector_name))}", which is illegal.
                ''')
        if (data_asset_name is None):
            raise ValueError('A valid data_asset_name must be specified.')
        if (data_asset_name and (not isinstance(data_asset_name, str))):
            raise TypeError(f'''The type of a data_asset name must be a string (Python "str").  The type given is
"{str(type(data_asset_name))}", which is illegal.
                ''')
        if (batch_identifiers and (not isinstance(batch_identifiers, IDDict))):
            raise TypeError(f'''The type of batch_identifiers must be an IDDict object.  The type given is "{str(type(batch_identifiers))}", which is illegal.
''')

    @property
    def datasource_name(self) -> str:
        import inspect
        __frame = inspect.currentframe()
        __file = __frame.f_code.co_filename
        __func = __frame.f_code.co_name
        for (k, v) in __frame.f_locals.items():
            if any(((var in k) for var in ('self', 'cls', '__frame', '__file', '__func'))):
                continue
            print(f'<INTROSPECT> {__file}:{__func}:{k} - {v.__class__.__name__}')
        return self._datasource_name

    @property
    def data_connector_name(self) -> str:
        import inspect
        __frame = inspect.currentframe()
        __file = __frame.f_code.co_filename
        __func = __frame.f_code.co_name
        for (k, v) in __frame.f_locals.items():
            if any(((var in k) for var in ('self', 'cls', '__frame', '__file', '__func'))):
                continue
            print(f'<INTROSPECT> {__file}:{__func}:{k} - {v.__class__.__name__}')
        return self._data_connector_name

    @property
    def data_asset_name(self) -> str:
        import inspect
        __frame = inspect.currentframe()
        __file = __frame.f_code.co_filename
        __func = __frame.f_code.co_name
        for (k, v) in __frame.f_locals.items():
            if any(((var in k) for var in ('self', 'cls', '__frame', '__file', '__func'))):
                continue
            print(f'<INTROSPECT> {__file}:{__func}:{k} - {v.__class__.__name__}')
        return self._data_asset_name

    @property
    def batch_identifiers(self) -> IDDict:
        import inspect
        __frame = inspect.currentframe()
        __file = __frame.f_code.co_filename
        __func = __frame.f_code.co_name
        for (k, v) in __frame.f_locals.items():
            if any(((var in k) for var in ('self', 'cls', '__frame', '__file', '__func'))):
                continue
            print(f'<INTROSPECT> {__file}:{__func}:{k} - {v.__class__.__name__}')
        return self._batch_identifiers

    @property
    def batch_spec_passthrough(self) -> dict:
        import inspect
        __frame = inspect.currentframe()
        __file = __frame.f_code.co_filename
        __func = __frame.f_code.co_name
        for (k, v) in __frame.f_locals.items():
            if any(((var in k) for var in ('self', 'cls', '__frame', '__file', '__func'))):
                continue
            print(f'<INTROSPECT> {__file}:{__func}:{k} - {v.__class__.__name__}')
        return self._batch_spec_passthrough

    @batch_spec_passthrough.setter
    def batch_spec_passthrough(self, batch_spec_passthrough: Optional[dict]) -> None:
        import inspect
        __frame = inspect.currentframe()
        __file = __frame.f_code.co_filename
        __func = __frame.f_code.co_name
        for (k, v) in __frame.f_locals.items():
            if any(((var in k) for var in ('self', 'cls', '__frame', '__file', '__func'))):
                continue
            print(f'<INTROSPECT> {__file}:{__func}:{k} - {v.__class__.__name__}')
        self._batch_spec_passthrough = batch_spec_passthrough

    @property
    def id(self) -> str:
        import inspect
        __frame = inspect.currentframe()
        __file = __frame.f_code.co_filename
        __func = __frame.f_code.co_name
        for (k, v) in __frame.f_locals.items():
            if any(((var in k) for var in ('self', 'cls', '__frame', '__file', '__func'))):
                continue
            print(f'<INTROSPECT> {__file}:{__func}:{k} - {v.__class__.__name__}')
        return IDDict(self.to_json_dict()).to_id()

    def __eq__(self, other):
        import inspect
        __frame = inspect.currentframe()
        __file = __frame.f_code.co_filename
        __func = __frame.f_code.co_name
        for (k, v) in __frame.f_locals.items():
            if any(((var in k) for var in ('self', 'cls', '__frame', '__file', '__func'))):
                continue
            print(f'<INTROSPECT> {__file}:{__func}:{k} - {v.__class__.__name__}')
        if (not isinstance(other, self.__class__)):
            return NotImplemented
        return (self.id == other.id)

    def __str__(self):
        import inspect
        __frame = inspect.currentframe()
        __file = __frame.f_code.co_filename
        __func = __frame.f_code.co_name
        for (k, v) in __frame.f_locals.items():
            if any(((var in k) for var in ('self', 'cls', '__frame', '__file', '__func'))):
                continue
            print(f'<INTROSPECT> {__file}:{__func}:{k} - {v.__class__.__name__}')
        return json.dumps(self.to_json_dict(), indent=2)

    def __hash__(self) -> int:
        import inspect
        __frame = inspect.currentframe()
        __file = __frame.f_code.co_filename
        __func = __frame.f_code.co_name
        for (k, v) in __frame.f_locals.items():
            if any(((var in k) for var in ('self', 'cls', '__frame', '__file', '__func'))):
                continue
            print(f'<INTROSPECT> {__file}:{__func}:{k} - {v.__class__.__name__}')
        'Overrides the default implementation'
        _result_hash: int = hash(self.id)
        return _result_hash

class BatchRequestBase(SerializableDictDot):
    '\n    This class is for internal inter-object protocol purposes only.\n    As such, it contains all attributes of a batch_request, but does not validate them.\n    See the BatchRequest class, which extends BatchRequestBase and validates the attributes.\n\n    BatchRequestBase is used for the internal protocol purposes exclusively, not part of API for the developer users.\n\n    Previously, the very same BatchRequest was used for both the internal protocol purposes and as part of the API\n    exposed to developers.  However, while convenient for internal data interchange, using the same BatchRequest class\n    as arguments to the externally-exported DataContext.get_batch(), DataContext.get_batch_list(), and\n    DataContext.get_validator() API calls for obtaining batches and/or validators was insufficiently expressive to\n    fulfill the needs of both. In the user-accessible API, BatchRequest, must enforce that all members of the triple,\n    consisting of data_source_name, data_connector_name, and data_asset_name, are not NULL.  Whereas for the internal\n    protocol, BatchRequest is used as a flexible bag of attributes, in which any fields are allowed to be NULL.  Hence,\n    now, BatchRequestBase is dedicated for the use as the bag oof attributes for the internal protocol use, whereby NULL\n    values are allowed as per the internal needs.  The BatchRequest class extends BatchRequestBase and adds to it strong\n    validation (described above plus additional attribute validation) so as to formally validate user specified fields.\n    '

    def __init__(self, datasource_name: str, data_connector_name: str, data_asset_name: str, data_connector_query: Optional[dict]=None, limit: Optional[int]=None, runtime_parameters: Optional[dict]=None, batch_identifiers: Optional[dict]=None, batch_spec_passthrough: Optional[dict]=None) -> None:
        import inspect
        __frame = inspect.currentframe()
        __file = __frame.f_code.co_filename
        __func = __frame.f_code.co_name
        for (k, v) in __frame.f_locals.items():
            if any(((var in k) for var in ('self', 'cls', '__frame', '__file', '__func'))):
                continue
            print(f'<INTROSPECT> {__file}:{__func}:{k} - {v.__class__.__name__}')
        self._datasource_name = datasource_name
        self._data_connector_name = data_connector_name
        self._data_asset_name = data_asset_name
        self._data_connector_query = data_connector_query
        self._limit = limit
        self._runtime_parameters = runtime_parameters
        self._batch_identifiers = batch_identifiers
        self._batch_spec_passthrough = batch_spec_passthrough

    @property
    def datasource_name(self) -> str:
        import inspect
        __frame = inspect.currentframe()
        __file = __frame.f_code.co_filename
        __func = __frame.f_code.co_name
        for (k, v) in __frame.f_locals.items():
            if any(((var in k) for var in ('self', 'cls', '__frame', '__file', '__func'))):
                continue
            print(f'<INTROSPECT> {__file}:{__func}:{k} - {v.__class__.__name__}')
        return self._datasource_name

    @datasource_name.setter
    def datasource_name(self, value: str) -> None:
        import inspect
        __frame = inspect.currentframe()
        __file = __frame.f_code.co_filename
        __func = __frame.f_code.co_name
        for (k, v) in __frame.f_locals.items():
            if any(((var in k) for var in ('self', 'cls', '__frame', '__file', '__func'))):
                continue
            print(f'<INTROSPECT> {__file}:{__func}:{k} - {v.__class__.__name__}')
        self._datasource_name = value

    @property
    def data_connector_name(self) -> str:
        import inspect
        __frame = inspect.currentframe()
        __file = __frame.f_code.co_filename
        __func = __frame.f_code.co_name
        for (k, v) in __frame.f_locals.items():
            if any(((var in k) for var in ('self', 'cls', '__frame', '__file', '__func'))):
                continue
            print(f'<INTROSPECT> {__file}:{__func}:{k} - {v.__class__.__name__}')
        return self._data_connector_name

    @data_connector_name.setter
    def data_connector_name(self, value: str) -> None:
        import inspect
        __frame = inspect.currentframe()
        __file = __frame.f_code.co_filename
        __func = __frame.f_code.co_name
        for (k, v) in __frame.f_locals.items():
            if any(((var in k) for var in ('self', 'cls', '__frame', '__file', '__func'))):
                continue
            print(f'<INTROSPECT> {__file}:{__func}:{k} - {v.__class__.__name__}')
        self._data_connector_name = value

    @property
    def data_asset_name(self) -> str:
        import inspect
        __frame = inspect.currentframe()
        __file = __frame.f_code.co_filename
        __func = __frame.f_code.co_name
        for (k, v) in __frame.f_locals.items():
            if any(((var in k) for var in ('self', 'cls', '__frame', '__file', '__func'))):
                continue
            print(f'<INTROSPECT> {__file}:{__func}:{k} - {v.__class__.__name__}')
        return self._data_asset_name

    @data_asset_name.setter
    def data_asset_name(self, data_asset_name) -> None:
        import inspect
        __frame = inspect.currentframe()
        __file = __frame.f_code.co_filename
        __func = __frame.f_code.co_name
        for (k, v) in __frame.f_locals.items():
            if any(((var in k) for var in ('self', 'cls', '__frame', '__file', '__func'))):
                continue
            print(f'<INTROSPECT> {__file}:{__func}:{k} - {v.__class__.__name__}')
        self._data_asset_name = data_asset_name

    @property
    def data_connector_query(self) -> dict:
        import inspect
        __frame = inspect.currentframe()
        __file = __frame.f_code.co_filename
        __func = __frame.f_code.co_name
        for (k, v) in __frame.f_locals.items():
            if any(((var in k) for var in ('self', 'cls', '__frame', '__file', '__func'))):
                continue
            print(f'<INTROSPECT> {__file}:{__func}:{k} - {v.__class__.__name__}')
        return self._data_connector_query

    @data_connector_query.setter
    def data_connector_query(self, value: dict) -> None:
        import inspect
        __frame = inspect.currentframe()
        __file = __frame.f_code.co_filename
        __func = __frame.f_code.co_name
        for (k, v) in __frame.f_locals.items():
            if any(((var in k) for var in ('self', 'cls', '__frame', '__file', '__func'))):
                continue
            print(f'<INTROSPECT> {__file}:{__func}:{k} - {v.__class__.__name__}')
        self._data_connector_query = value

    @property
    def limit(self) -> int:
        import inspect
        __frame = inspect.currentframe()
        __file = __frame.f_code.co_filename
        __func = __frame.f_code.co_name
        for (k, v) in __frame.f_locals.items():
            if any(((var in k) for var in ('self', 'cls', '__frame', '__file', '__func'))):
                continue
            print(f'<INTROSPECT> {__file}:{__func}:{k} - {v.__class__.__name__}')
        return self._limit

    @limit.setter
    def limit(self, value: int) -> None:
        import inspect
        __frame = inspect.currentframe()
        __file = __frame.f_code.co_filename
        __func = __frame.f_code.co_name
        for (k, v) in __frame.f_locals.items():
            if any(((var in k) for var in ('self', 'cls', '__frame', '__file', '__func'))):
                continue
            print(f'<INTROSPECT> {__file}:{__func}:{k} - {v.__class__.__name__}')
        self._limit = value

    @property
    def runtime_parameters(self) -> dict:
        import inspect
        __frame = inspect.currentframe()
        __file = __frame.f_code.co_filename
        __func = __frame.f_code.co_name
        for (k, v) in __frame.f_locals.items():
            if any(((var in k) for var in ('self', 'cls', '__frame', '__file', '__func'))):
                continue
            print(f'<INTROSPECT> {__file}:{__func}:{k} - {v.__class__.__name__}')
        return self._runtime_parameters

    @runtime_parameters.setter
    def runtime_parameters(self, value: dict) -> None:
        import inspect
        __frame = inspect.currentframe()
        __file = __frame.f_code.co_filename
        __func = __frame.f_code.co_name
        for (k, v) in __frame.f_locals.items():
            if any(((var in k) for var in ('self', 'cls', '__frame', '__file', '__func'))):
                continue
            print(f'<INTROSPECT> {__file}:{__func}:{k} - {v.__class__.__name__}')
        self._runtime_parameters = value

    @property
    def batch_identifiers(self) -> dict:
        import inspect
        __frame = inspect.currentframe()
        __file = __frame.f_code.co_filename
        __func = __frame.f_code.co_name
        for (k, v) in __frame.f_locals.items():
            if any(((var in k) for var in ('self', 'cls', '__frame', '__file', '__func'))):
                continue
            print(f'<INTROSPECT> {__file}:{__func}:{k} - {v.__class__.__name__}')
        return self._batch_identifiers

    @batch_identifiers.setter
    def batch_identifiers(self, value: dict) -> None:
        import inspect
        __frame = inspect.currentframe()
        __file = __frame.f_code.co_filename
        __func = __frame.f_code.co_name
        for (k, v) in __frame.f_locals.items():
            if any(((var in k) for var in ('self', 'cls', '__frame', '__file', '__func'))):
                continue
            print(f'<INTROSPECT> {__file}:{__func}:{k} - {v.__class__.__name__}')
        self._batch_identifiers = value

    @property
    def batch_spec_passthrough(self) -> dict:
        import inspect
        __frame = inspect.currentframe()
        __file = __frame.f_code.co_filename
        __func = __frame.f_code.co_name
        for (k, v) in __frame.f_locals.items():
            if any(((var in k) for var in ('self', 'cls', '__frame', '__file', '__func'))):
                continue
            print(f'<INTROSPECT> {__file}:{__func}:{k} - {v.__class__.__name__}')
        return self._batch_spec_passthrough

    @batch_spec_passthrough.setter
    def batch_spec_passthrough(self, value: dict) -> None:
        import inspect
        __frame = inspect.currentframe()
        __file = __frame.f_code.co_filename
        __func = __frame.f_code.co_name
        for (k, v) in __frame.f_locals.items():
            if any(((var in k) for var in ('self', 'cls', '__frame', '__file', '__func'))):
                continue
            print(f'<INTROSPECT> {__file}:{__func}:{k} - {v.__class__.__name__}')
        self._batch_spec_passthrough = value

    @property
    def id(self) -> str:
        import inspect
        __frame = inspect.currentframe()
        __file = __frame.f_code.co_filename
        __func = __frame.f_code.co_name
        for (k, v) in __frame.f_locals.items():
            if any(((var in k) for var in ('self', 'cls', '__frame', '__file', '__func'))):
                continue
            print(f'<INTROSPECT> {__file}:{__func}:{k} - {v.__class__.__name__}')
        return IDDict(self.to_json_dict()).to_id()

    def to_dict(self) -> dict:
        import inspect
        __frame = inspect.currentframe()
        __file = __frame.f_code.co_filename
        __func = __frame.f_code.co_name
        for (k, v) in __frame.f_locals.items():
            if any(((var in k) for var in ('self', 'cls', '__frame', '__file', '__func'))):
                continue
            print(f'<INTROSPECT> {__file}:{__func}:{k} - {v.__class__.__name__}')
        return standardize_batch_request_display_ordering(batch_request=super().to_dict())

    def to_json_dict(self) -> dict:
        import inspect
        __frame = inspect.currentframe()
        __file = __frame.f_code.co_filename
        __func = __frame.f_code.co_name
        for (k, v) in __frame.f_locals.items():
            if any(((var in k) for var in ('self', 'cls', '__frame', '__file', '__func'))):
                continue
            print(f'<INTROSPECT> {__file}:{__func}:{k} - {v.__class__.__name__}')
        '\n        # TODO: <Alex>2/4/2022</Alex>\n        This implementation of "SerializableDictDot.to_json_dict() occurs frequently and should ideally serve as the\n        reference implementation in the "SerializableDictDot" class itself.  However, the circular import dependencies,\n        due to the location of the "great_expectations/types/__init__.py" and "great_expectations/core/util.py" modules\n        make this refactoring infeasible at the present time.\n        '
        if batch_request_contains_batch_data(batch_request=self):
            batch_data: Union[(BatchRequestBase, dict)] = self.runtime_parameters['batch_data']
            self.runtime_parameters['batch_data']: str = str(type(batch_data))
            serializeable_dict: dict = convert_to_json_serializable(data=self.to_dict())
            self.runtime_parameters['batch_data']: Union[(BatchRequestBase, dict)] = batch_data
        else:
            serializeable_dict: dict = convert_to_json_serializable(data=self.to_dict())
        return serializeable_dict

    def __deepcopy__(self, memo):
        import inspect
        __frame = inspect.currentframe()
        __file = __frame.f_code.co_filename
        __func = __frame.f_code.co_name
        for (k, v) in __frame.f_locals.items():
            if any(((var in k) for var in ('self', 'cls', '__frame', '__file', '__func'))):
                continue
            print(f'<INTROSPECT> {__file}:{__func}:{k} - {v.__class__.__name__}')
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        for (key, value) in self.to_raw_dict().items():
            value_copy = safe_deep_copy(data=value, memo=memo)
            setattr(result, key, value_copy)
        return result

    def __eq__(self, other):
        import inspect
        __frame = inspect.currentframe()
        __file = __frame.f_code.co_filename
        __func = __frame.f_code.co_name
        for (k, v) in __frame.f_locals.items():
            if any(((var in k) for var in ('self', 'cls', '__frame', '__file', '__func'))):
                continue
            print(f'<INTROSPECT> {__file}:{__func}:{k} - {v.__class__.__name__}')
        if (not isinstance(other, self.__class__)):
            return NotImplemented
        return (self.id == other.id)

    def __repr__(self) -> str:
        import inspect
        __frame = inspect.currentframe()
        __file = __frame.f_code.co_filename
        __func = __frame.f_code.co_name
        for (k, v) in __frame.f_locals.items():
            if any(((var in k) for var in ('self', 'cls', '__frame', '__file', '__func'))):
                continue
            print(f'<INTROSPECT> {__file}:{__func}:{k} - {v.__class__.__name__}')
        '\n        # TODO: <Alex>2/4/2022</Alex>\n        This implementation of a custom "__repr__()" occurs frequently and should ideally serve as the reference\n        implementation in the "SerializableDictDot" class.  However, the circular import dependencies, due to the\n        location of the "great_expectations/types/__init__.py" and "great_expectations/core/util.py" modules make this\n        refactoring infeasible at the present time.\n        '
        json_dict: dict = self.to_json_dict()
        deep_filter_properties_iterable(properties=json_dict, inplace=True)
        return json.dumps(json_dict, indent=2)

    def __str__(self) -> str:
        import inspect
        __frame = inspect.currentframe()
        __file = __frame.f_code.co_filename
        __func = __frame.f_code.co_name
        for (k, v) in __frame.f_locals.items():
            if any(((var in k) for var in ('self', 'cls', '__frame', '__file', '__func'))):
                continue
            print(f'<INTROSPECT> {__file}:{__func}:{k} - {v.__class__.__name__}')
        '\n        # TODO: <Alex>2/4/2022</Alex>\n        This implementation of a custom "__str__()" occurs frequently and should ideally serve as the reference\n        implementation in the "SerializableDictDot" class.  However, the circular import dependencies, due to the\n        location of the "great_expectations/types/__init__.py" and "great_expectations/core/util.py" modules make this\n        refactoring infeasible at the present time.\n        '
        return self.__repr__()

    @staticmethod
    def _validate_init_parameters(datasource_name: str, data_connector_name: str, data_asset_name: str, data_connector_query: Optional[dict]=None, limit: Optional[int]=None) -> None:
        import inspect
        __frame = inspect.currentframe()
        __file = __frame.f_code.co_filename
        __func = __frame.f_code.co_name
        for (k, v) in __frame.f_locals.items():
            if any(((var in k) for var in ('self', 'cls', '__frame', '__file', '__func'))):
                continue
            print(f'<INTROSPECT> {__file}:{__func}:{k} - {v.__class__.__name__}')
        if (not (datasource_name and isinstance(datasource_name, str))):
            raise TypeError(f'''The type of an datasource name must be a string (Python "str").  The type given is
"{str(type(datasource_name))}", which is illegal.
            ''')
        if (not (data_connector_name and isinstance(data_connector_name, str))):
            raise TypeError(f'''The type of data_connector name must be a string (Python "str").  The type given is
"{str(type(data_connector_name))}", which is illegal.
                ''')
        if (not (data_asset_name and isinstance(data_asset_name, str))):
            raise TypeError(f'''The type of data_asset name must be a string (Python "str").  The type given is
        "{str(type(data_asset_name))}", which is illegal.
                        ''')
        if (data_connector_query and (not isinstance(data_connector_query, dict))):
            raise TypeError(f'''The type of data_connector_query must be a dict object.  The type given is
"{str(type(data_connector_query))}", which is illegal.
                ''')
        if (limit and (not isinstance(limit, int))):
            raise TypeError(f'''The type of limit must be an integer (Python "int").  The type given is "{str(type(limit))}", which
is illegal.
                ''')

class BatchRequest(BatchRequestBase):
    '\n    This class contains all attributes of a batch_request.  See the comments in BatchRequestBase for design specifics.\n    limit: refers to the number of batches requested (not rows per batch)\n    '
    include_field_names: Set[str] = {'datasource_name', 'data_connector_name', 'data_asset_name', 'data_connector_query', 'limit', 'batch_spec_passthrough'}

    def __init__(self, datasource_name: str, data_connector_name: str, data_asset_name: str, data_connector_query: Optional[dict]=None, limit: Optional[int]=None, batch_spec_passthrough: Optional[dict]=None) -> None:
        import inspect
        __frame = inspect.currentframe()
        __file = __frame.f_code.co_filename
        __func = __frame.f_code.co_name
        for (k, v) in __frame.f_locals.items():
            if any(((var in k) for var in ('self', 'cls', '__frame', '__file', '__func'))):
                continue
            print(f'<INTROSPECT> {__file}:{__func}:{k} - {v.__class__.__name__}')
        self._validate_init_parameters(datasource_name=datasource_name, data_connector_name=data_connector_name, data_asset_name=data_asset_name, data_connector_query=data_connector_query, limit=limit)
        super().__init__(datasource_name=datasource_name, data_connector_name=data_connector_name, data_asset_name=data_asset_name, data_connector_query=data_connector_query, limit=limit, batch_spec_passthrough=batch_spec_passthrough)

class RuntimeBatchRequest(BatchRequestBase):
    include_field_names: Set[str] = {'datasource_name', 'data_connector_name', 'data_asset_name', 'runtime_parameters', 'batch_identifiers', 'batch_spec_passthrough'}

    def __init__(self, datasource_name: str, data_connector_name: str, data_asset_name: str, runtime_parameters: dict, batch_identifiers: dict, batch_spec_passthrough: Optional[dict]=None) -> None:
        import inspect
        __frame = inspect.currentframe()
        __file = __frame.f_code.co_filename
        __func = __frame.f_code.co_name
        for (k, v) in __frame.f_locals.items():
            if any(((var in k) for var in ('self', 'cls', '__frame', '__file', '__func'))):
                continue
            print(f'<INTROSPECT> {__file}:{__func}:{k} - {v.__class__.__name__}')
        self._validate_init_parameters(datasource_name=datasource_name, data_connector_name=data_connector_name, data_asset_name=data_asset_name)
        self._validate_runtime_batch_request_specific_init_parameters(runtime_parameters=runtime_parameters, batch_identifiers=batch_identifiers, batch_spec_passthrough=batch_spec_passthrough)
        super().__init__(datasource_name=datasource_name, data_connector_name=data_connector_name, data_asset_name=data_asset_name, runtime_parameters=runtime_parameters, batch_identifiers=batch_identifiers, batch_spec_passthrough=batch_spec_passthrough)

    @staticmethod
    def _validate_runtime_batch_request_specific_init_parameters(runtime_parameters: dict, batch_identifiers: dict, batch_spec_passthrough: Optional[dict]=None) -> None:
        import inspect
        __frame = inspect.currentframe()
        __file = __frame.f_code.co_filename
        __func = __frame.f_code.co_name
        for (k, v) in __frame.f_locals.items():
            if any(((var in k) for var in ('self', 'cls', '__frame', '__file', '__func'))):
                continue
            print(f'<INTROSPECT> {__file}:{__func}:{k} - {v.__class__.__name__}')
        if (not (runtime_parameters and isinstance(runtime_parameters, dict))):
            raise TypeError(f'''The runtime_parameters must be a non-empty dict object.
                The type given is "{str(type(runtime_parameters))}", which is an illegal type or an empty dictionary.''')
        if (not (batch_identifiers and isinstance(batch_identifiers, dict))):
            raise TypeError(f'''The type for batch_identifiers must be a dict object, with keys being identifiers defined in the
                data connector configuration.  The type given is "{str(type(batch_identifiers))}", which is illegal.''')
        if (batch_spec_passthrough and (not isinstance(batch_spec_passthrough, dict))):
            raise TypeError(f'''The type for batch_spec_passthrough must be a dict object. The type given is "{str(type(batch_spec_passthrough))}", which is illegal.
''')

class BatchMarkers(BatchKwargs):
    "A BatchMarkers is a special type of BatchKwargs (so that it has a batch_fingerprint) but it generally does\n    NOT require specific keys and instead captures information about the OUTPUT of a datasource's fetch\n    process, such as the timestamp at which a query was executed."

    def __init__(self, *args, **kwargs) -> None:
        import inspect
        __frame = inspect.currentframe()
        __file = __frame.f_code.co_filename
        __func = __frame.f_code.co_name
        for (k, v) in __frame.f_locals.items():
            if any(((var in k) for var in ('self', 'cls', '__frame', '__file', '__func'))):
                continue
            print(f'<INTROSPECT> {__file}:{__func}:{k} - {v.__class__.__name__}')
        super().__init__(*args, **kwargs)
        if ('ge_load_time' not in self):
            raise InvalidBatchIdError('BatchMarkers requires a ge_load_time')

    @property
    def ge_load_time(self):
        import inspect
        __frame = inspect.currentframe()
        __file = __frame.f_code.co_filename
        __func = __frame.f_code.co_name
        for (k, v) in __frame.f_locals.items():
            if any(((var in k) for var in ('self', 'cls', '__frame', '__file', '__func'))):
                continue
            print(f'<INTROSPECT> {__file}:{__func}:{k} - {v.__class__.__name__}')
        return self.get('ge_load_time')

class Batch(SerializableDictDot):

    def __init__(self, data, batch_request: Optional[Union[(BatchRequestBase, dict)]]=None, batch_definition: BatchDefinition=None, batch_spec: BatchSpec=None, batch_markers: BatchMarkers=None, data_context=None, datasource_name=None, batch_parameters=None, batch_kwargs=None) -> None:
        import inspect
        __frame = inspect.currentframe()
        __file = __frame.f_code.co_filename
        __func = __frame.f_code.co_name
        for (k, v) in __frame.f_locals.items():
            if any(((var in k) for var in ('self', 'cls', '__frame', '__file', '__func'))):
                continue
            print(f'<INTROSPECT> {__file}:{__func}:{k} - {v.__class__.__name__}')
        self._data = data
        if (batch_request is None):
            batch_request = {}
        self._batch_request = batch_request
        if (batch_definition is None):
            batch_definition = IDDict()
        self._batch_definition = batch_definition
        if (batch_spec is None):
            batch_spec = BatchSpec()
        self._batch_spec = batch_spec
        if (batch_markers is None):
            batch_markers = BatchMarkers({'ge_load_time': datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')})
        self._batch_markers = batch_markers
        self._data_context = data_context
        self._datasource_name = datasource_name
        self._batch_parameters = batch_parameters
        self._batch_kwargs = (batch_kwargs or BatchKwargs())

    @property
    def data(self):
        import inspect
        __frame = inspect.currentframe()
        __file = __frame.f_code.co_filename
        __func = __frame.f_code.co_name
        for (k, v) in __frame.f_locals.items():
            if any(((var in k) for var in ('self', 'cls', '__frame', '__file', '__func'))):
                continue
            print(f'<INTROSPECT> {__file}:{__func}:{k} - {v.__class__.__name__}')
        return self._data

    @property
    def batch_request(self):
        import inspect
        __frame = inspect.currentframe()
        __file = __frame.f_code.co_filename
        __func = __frame.f_code.co_name
        for (k, v) in __frame.f_locals.items():
            if any(((var in k) for var in ('self', 'cls', '__frame', '__file', '__func'))):
                continue
            print(f'<INTROSPECT> {__file}:{__func}:{k} - {v.__class__.__name__}')
        return self._batch_request

    @batch_request.setter
    def batch_request(self, batch_request) -> None:
        import inspect
        __frame = inspect.currentframe()
        __file = __frame.f_code.co_filename
        __func = __frame.f_code.co_name
        for (k, v) in __frame.f_locals.items():
            if any(((var in k) for var in ('self', 'cls', '__frame', '__file', '__func'))):
                continue
            print(f'<INTROSPECT> {__file}:{__func}:{k} - {v.__class__.__name__}')
        self._batch_request = batch_request

    @property
    def batch_definition(self):
        import inspect
        __frame = inspect.currentframe()
        __file = __frame.f_code.co_filename
        __func = __frame.f_code.co_name
        for (k, v) in __frame.f_locals.items():
            if any(((var in k) for var in ('self', 'cls', '__frame', '__file', '__func'))):
                continue
            print(f'<INTROSPECT> {__file}:{__func}:{k} - {v.__class__.__name__}')
        return self._batch_definition

    @batch_definition.setter
    def batch_definition(self, batch_definition) -> None:
        import inspect
        __frame = inspect.currentframe()
        __file = __frame.f_code.co_filename
        __func = __frame.f_code.co_name
        for (k, v) in __frame.f_locals.items():
            if any(((var in k) for var in ('self', 'cls', '__frame', '__file', '__func'))):
                continue
            print(f'<INTROSPECT> {__file}:{__func}:{k} - {v.__class__.__name__}')
        self._batch_definition = batch_definition

    @property
    def batch_spec(self):
        import inspect
        __frame = inspect.currentframe()
        __file = __frame.f_code.co_filename
        __func = __frame.f_code.co_name
        for (k, v) in __frame.f_locals.items():
            if any(((var in k) for var in ('self', 'cls', '__frame', '__file', '__func'))):
                continue
            print(f'<INTROSPECT> {__file}:{__func}:{k} - {v.__class__.__name__}')
        return self._batch_spec

    @property
    def batch_markers(self):
        import inspect
        __frame = inspect.currentframe()
        __file = __frame.f_code.co_filename
        __func = __frame.f_code.co_name
        for (k, v) in __frame.f_locals.items():
            if any(((var in k) for var in ('self', 'cls', '__frame', '__file', '__func'))):
                continue
            print(f'<INTROSPECT> {__file}:{__func}:{k} - {v.__class__.__name__}')
        return self._batch_markers

    @property
    def data_context(self):
        import inspect
        __frame = inspect.currentframe()
        __file = __frame.f_code.co_filename
        __func = __frame.f_code.co_name
        for (k, v) in __frame.f_locals.items():
            if any(((var in k) for var in ('self', 'cls', '__frame', '__file', '__func'))):
                continue
            print(f'<INTROSPECT> {__file}:{__func}:{k} - {v.__class__.__name__}')
        return self._data_context

    @property
    def datasource_name(self):
        import inspect
        __frame = inspect.currentframe()
        __file = __frame.f_code.co_filename
        __func = __frame.f_code.co_name
        for (k, v) in __frame.f_locals.items():
            if any(((var in k) for var in ('self', 'cls', '__frame', '__file', '__func'))):
                continue
            print(f'<INTROSPECT> {__file}:{__func}:{k} - {v.__class__.__name__}')
        return self._datasource_name

    @property
    def batch_parameters(self):
        import inspect
        __frame = inspect.currentframe()
        __file = __frame.f_code.co_filename
        __func = __frame.f_code.co_name
        for (k, v) in __frame.f_locals.items():
            if any(((var in k) for var in ('self', 'cls', '__frame', '__file', '__func'))):
                continue
            print(f'<INTROSPECT> {__file}:{__func}:{k} - {v.__class__.__name__}')
        return self._batch_parameters

    @property
    def batch_kwargs(self):
        import inspect
        __frame = inspect.currentframe()
        __file = __frame.f_code.co_filename
        __func = __frame.f_code.co_name
        for (k, v) in __frame.f_locals.items():
            if any(((var in k) for var in ('self', 'cls', '__frame', '__file', '__func'))):
                continue
            print(f'<INTROSPECT> {__file}:{__func}:{k} - {v.__class__.__name__}')
        return self._batch_kwargs

    def to_dict(self) -> dict:
        import inspect
        __frame = inspect.currentframe()
        __file = __frame.f_code.co_filename
        __func = __frame.f_code.co_name
        for (k, v) in __frame.f_locals.items():
            if any(((var in k) for var in ('self', 'cls', '__frame', '__file', '__func'))):
                continue
            print(f'<INTROSPECT> {__file}:{__func}:{k} - {v.__class__.__name__}')
        dict_obj: dict = {'data': str(self.data), 'batch_request': self.batch_request.to_dict(), 'batch_definition': (self.batch_definition.to_json_dict() if isinstance(self.batch_definition, BatchDefinition) else {}), 'batch_spec': self.batch_spec, 'batch_markers': self.batch_markers}
        return dict_obj

    def to_json_dict(self) -> dict:
        import inspect
        __frame = inspect.currentframe()
        __file = __frame.f_code.co_filename
        __func = __frame.f_code.co_name
        for (k, v) in __frame.f_locals.items():
            if any(((var in k) for var in ('self', 'cls', '__frame', '__file', '__func'))):
                continue
            print(f'<INTROSPECT> {__file}:{__func}:{k} - {v.__class__.__name__}')
        json_dict: dict = self.to_dict()
        deep_filter_properties_iterable(properties=json_dict['batch_request'], inplace=True)
        return json_dict

    @property
    def id(self):
        import inspect
        __frame = inspect.currentframe()
        __file = __frame.f_code.co_filename
        __func = __frame.f_code.co_name
        for (k, v) in __frame.f_locals.items():
            if any(((var in k) for var in ('self', 'cls', '__frame', '__file', '__func'))):
                continue
            print(f'<INTROSPECT> {__file}:{__func}:{k} - {v.__class__.__name__}')
        batch_definition = self._batch_definition
        return (batch_definition.id if isinstance(batch_definition, BatchDefinition) else batch_definition.to_id())

    def __str__(self):
        import inspect
        __frame = inspect.currentframe()
        __file = __frame.f_code.co_filename
        __func = __frame.f_code.co_name
        for (k, v) in __frame.f_locals.items():
            if any(((var in k) for var in ('self', 'cls', '__frame', '__file', '__func'))):
                continue
            print(f'<INTROSPECT> {__file}:{__func}:{k} - {v.__class__.__name__}')
        return json.dumps(self.to_json_dict(), indent=2)

    def head(self, n_rows=5, fetch_all=False):
        import inspect
        __frame = inspect.currentframe()
        __file = __frame.f_code.co_filename
        __func = __frame.f_code.co_name
        for (k, v) in __frame.f_locals.items():
            if any(((var in k) for var in ('self', 'cls', '__frame', '__file', '__func'))):
                continue
            print(f'<INTROSPECT> {__file}:{__func}:{k} - {v.__class__.__name__}')
        metric = MetricConfiguration('table.head', {'batch_id': self.id}, {'n_rows': n_rows, 'fetch_all': fetch_all})
        return self._data.execution_engine.resolve_metrics((metric,))[metric.id]

def materialize_batch_request(batch_request: Optional[Union[(BatchRequestBase, dict)]]=None) -> Optional[BatchRequestBase]:
    import inspect
    __frame = inspect.currentframe()
    __file = __frame.f_code.co_filename
    __func = __frame.f_code.co_name
    for (k, v) in __frame.f_locals.items():
        if any(((var in k) for var in ('self', 'cls', '__frame', '__file', '__func'))):
            continue
        print(f'<INTROSPECT> {__file}:{__func}:{k} - {v.__class__.__name__}')
    effective_batch_request: dict = get_batch_request_as_dict(batch_request=batch_request)
    if (not effective_batch_request):
        return None
    batch_request_class: type
    if batch_request_contains_runtime_parameters(batch_request=effective_batch_request):
        batch_request_class = RuntimeBatchRequest
    else:
        batch_request_class = BatchRequest
    return batch_request_class(**effective_batch_request)

def batch_request_contains_batch_data(batch_request: Optional[Union[(BatchRequestBase, dict)]]=None) -> bool:
    import inspect
    __frame = inspect.currentframe()
    __file = __frame.f_code.co_filename
    __func = __frame.f_code.co_name
    for (k, v) in __frame.f_locals.items():
        if any(((var in k) for var in ('self', 'cls', '__frame', '__file', '__func'))):
            continue
        print(f'<INTROSPECT> {__file}:{__func}:{k} - {v.__class__.__name__}')
    return (batch_request_contains_runtime_parameters(batch_request=batch_request) and (batch_request['runtime_parameters'].get('batch_data') is not None))

def batch_request_contains_runtime_parameters(batch_request: Optional[Union[(BatchRequestBase, dict)]]=None) -> bool:
    import inspect
    __frame = inspect.currentframe()
    __file = __frame.f_code.co_filename
    __func = __frame.f_code.co_name
    for (k, v) in __frame.f_locals.items():
        if any(((var in k) for var in ('self', 'cls', '__frame', '__file', '__func'))):
            continue
        print(f'<INTROSPECT> {__file}:{__func}:{k} - {v.__class__.__name__}')
    return ((batch_request is not None) and isinstance(batch_request, (dict, DictDot)) and (batch_request.get('runtime_parameters') is not None))

def get_batch_request_as_dict(batch_request: Optional[Union[(BatchRequestBase, dict)]]=None) -> Optional[dict]:
    import inspect
    __frame = inspect.currentframe()
    __file = __frame.f_code.co_filename
    __func = __frame.f_code.co_name
    for (k, v) in __frame.f_locals.items():
        if any(((var in k) for var in ('self', 'cls', '__frame', '__file', '__func'))):
            continue
        print(f'<INTROSPECT> {__file}:{__func}:{k} - {v.__class__.__name__}')
    if (batch_request is None):
        return None
    if isinstance(batch_request, (BatchRequest, RuntimeBatchRequest)):
        batch_request = batch_request.to_dict()
    return batch_request

def get_batch_request_from_acceptable_arguments(datasource_name: Optional[str]=None, data_connector_name: Optional[str]=None, data_asset_name: Optional[str]=None, *, batch_request: Optional[BatchRequestBase]=None, batch_data: Optional[Any]=None, data_connector_query: Optional[dict]=None, batch_identifiers: Optional[dict]=None, limit: Optional[int]=None, index: Optional[Union[(int, list, tuple, slice, str)]]=None, custom_filter_function: Optional[Callable]=None, batch_spec_passthrough: Optional[dict]=None, sampling_method: Optional[str]=None, sampling_kwargs: Optional[dict]=None, splitter_method: Optional[str]=None, splitter_kwargs: Optional[dict]=None, runtime_parameters: Optional[dict]=None, query: Optional[str]=None, path: Optional[str]=None, batch_filter_parameters: Optional[dict]=None, **kwargs) -> Union[(BatchRequest, RuntimeBatchRequest)]:
    import inspect
    __frame = inspect.currentframe()
    __file = __frame.f_code.co_filename
    __func = __frame.f_code.co_name
    for (k, v) in __frame.f_locals.items():
        if any(((var in k) for var in ('self', 'cls', '__frame', '__file', '__func'))):
            continue
        print(f'<INTROSPECT> {__file}:{__func}:{k} - {v.__class__.__name__}')
    'Obtain formal BatchRequest typed object from allowed attributes (supplied as arguments).\n    This method applies only to the new (V3) Datasource schema.\n\n    Args:\n        datasource_name\n        data_connector_name\n        data_asset_name\n\n        batch_request\n        batch_data\n        query\n        path\n        runtime_parameters\n        data_connector_query\n        batch_identifiers\n        batch_filter_parameters\n\n        limit\n        index\n        custom_filter_function\n\n        sampling_method\n        sampling_kwargs\n\n        splitter_method\n        splitter_kwargs\n\n        batch_spec_passthrough\n\n        **kwargs\n\n    Returns:\n        (BatchRequest or RuntimeBatchRequest) The formal BatchRequest or RuntimeBatchRequest object\n    '
    if batch_request:
        if (not isinstance(batch_request, (BatchRequest, RuntimeBatchRequest))):
            raise TypeError(f'batch_request must be an instance of BatchRequest or RuntimeBatchRequest object, not {type(batch_request)}')
        datasource_name = batch_request.datasource_name
    if (not isinstance(datasource_name, str)):
        raise ge_exceptions.GreatExpectationsTypeError(f'the first parameter, datasource_name, must be a str, not {type(datasource_name)}')
    if (len([arg for arg in [batch_data, query, path] if (arg is not None)]) > 1):
        raise ValueError('Must provide only one of batch_data, query, or path.')
    if any([((batch_data is not None) and runtime_parameters and ('batch_data' in runtime_parameters)), (query and runtime_parameters and ('query' in runtime_parameters)), (path and runtime_parameters and ('path' in runtime_parameters))]):
        raise ValueError('If batch_data, query, or path arguments are provided, the same keys cannot appear in the runtime_parameters argument.')
    if batch_request:
        return batch_request
    batch_request_class: type
    batch_request_as_dict: dict
    if any([(batch_data is not None), query, path, runtime_parameters]):
        batch_request_class = RuntimeBatchRequest
        runtime_parameters = (runtime_parameters or {})
        if (batch_data is not None):
            runtime_parameters['batch_data'] = batch_data
        elif (query is not None):
            runtime_parameters['query'] = query
        elif (path is not None):
            runtime_parameters['path'] = path
        if (batch_identifiers is None):
            batch_identifiers = kwargs
        else:
            pass
        batch_request_as_dict = {'datasource_name': datasource_name, 'data_connector_name': data_connector_name, 'data_asset_name': data_asset_name, 'runtime_parameters': runtime_parameters, 'batch_identifiers': batch_identifiers, 'batch_spec_passthrough': batch_spec_passthrough}
    else:
        batch_request_class = BatchRequest
        if (data_connector_query is None):
            if ((batch_filter_parameters is not None) and (batch_identifiers is not None)):
                raise ValueError('Must provide either "batch_filter_parameters" or "batch_identifiers", not both.')
            if ((batch_filter_parameters is None) and (batch_identifiers is not None)):
                logger.warning('Attempting to build data_connector_query but "batch_identifiers" was provided instead of "batch_filter_parameters". The "batch_identifiers" key on data_connector_query has been renamed to "batch_filter_parameters". Please update your code. Falling back on provided "batch_identifiers".')
                batch_filter_parameters = batch_identifiers
            elif ((batch_filter_parameters is None) and (batch_identifiers is None)):
                batch_filter_parameters = kwargs
            else:
                pass
            data_connector_query_params: dict = {'batch_filter_parameters': batch_filter_parameters, 'limit': limit, 'index': index, 'custom_filter_function': custom_filter_function}
            data_connector_query = IDDict(data_connector_query_params)
        else:
            data_connector_query = IDDict(data_connector_query)
        if (batch_spec_passthrough is None):
            batch_spec_passthrough = {}
            if (sampling_method is not None):
                sampling_params: dict = {'sampling_method': sampling_method}
                if (sampling_kwargs is not None):
                    sampling_params['sampling_kwargs'] = sampling_kwargs
                batch_spec_passthrough.update(sampling_params)
            if (splitter_method is not None):
                splitter_params: dict = {'splitter_method': splitter_method}
                if (splitter_kwargs is not None):
                    splitter_params['splitter_kwargs'] = splitter_kwargs
                batch_spec_passthrough.update(splitter_params)
        batch_request_as_dict: dict = {'datasource_name': datasource_name, 'data_connector_name': data_connector_name, 'data_asset_name': data_asset_name, 'data_connector_query': data_connector_query, 'batch_spec_passthrough': batch_spec_passthrough}
    deep_filter_properties_iterable(properties=batch_request_as_dict, inplace=True)
    batch_request = batch_request_class(**batch_request_as_dict)
    return batch_request

def standardize_batch_request_display_ordering(batch_request: Dict[(str, Union[(str, int, Dict[(str, Any)])])]) -> Dict[(str, Union[(str, Dict[(str, Any)])])]:
    import inspect
    __frame = inspect.currentframe()
    __file = __frame.f_code.co_filename
    __func = __frame.f_code.co_name
    for (k, v) in __frame.f_locals.items():
        if any(((var in k) for var in ('self', 'cls', '__frame', '__file', '__func'))):
            continue
        print(f'<INTROSPECT> {__file}:{__func}:{k} - {v.__class__.__name__}')
    datasource_name: str = batch_request['datasource_name']
    data_connector_name: str = batch_request['data_connector_name']
    data_asset_name: str = batch_request['data_asset_name']
    runtime_parameters: str = batch_request.get('runtime_parameters')
    batch_identifiers: str = batch_request.get('batch_identifiers')
    batch_request.pop('datasource_name')
    batch_request.pop('data_connector_name')
    batch_request.pop('data_asset_name')
    if (runtime_parameters is not None):
        batch_request.pop('runtime_parameters')
    if (batch_identifiers is not None):
        batch_request.pop('batch_identifiers')
    if ((runtime_parameters is not None) and (batch_identifiers is not None)):
        batch_request = {'datasource_name': datasource_name, 'data_connector_name': data_connector_name, 'data_asset_name': data_asset_name, 'runtime_parameters': runtime_parameters, 'batch_identifiers': batch_identifiers, **batch_request}
    elif ((runtime_parameters is not None) and (batch_identifiers is None)):
        batch_request = {'datasource_name': datasource_name, 'data_connector_name': data_connector_name, 'data_asset_name': data_asset_name, 'runtime_parameters': runtime_parameters, **batch_request}
    elif ((runtime_parameters is None) and (batch_identifiers is not None)):
        batch_request = {'datasource_name': datasource_name, 'data_connector_name': data_connector_name, 'data_asset_name': data_asset_name, 'batch_identifiers': batch_identifiers, **batch_request}
    else:
        batch_request = {'datasource_name': datasource_name, 'data_connector_name': data_connector_name, 'data_asset_name': data_asset_name, **batch_request}
    return batch_request
