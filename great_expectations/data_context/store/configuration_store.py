
import logging
from typing import Optional, Union
from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap
import great_expectations.exceptions as ge_exceptions
from great_expectations.data_context.store.store import Store
from great_expectations.data_context.store.tuple_store_backend import TupleStoreBackend
from great_expectations.data_context.types.base import BaseYamlConfig
from great_expectations.data_context.types.resource_identifiers import ConfigurationIdentifier, GeCloudIdentifier
from great_expectations.data_context.util import load_class
from great_expectations.util import filter_properties_dict, verify_dynamic_loading_support
yaml = YAML()
yaml.indent(mapping=2, sequence=4, offset=2)
yaml.default_flow_style = False
logger = logging.getLogger(__name__)

class ConfigurationStore(Store):
    '\n    Configuration Store provides a way to store any Marshmallow Schema compatible Configuration (using the YAML format).\n    '
    _key_class = ConfigurationIdentifier
    _configuration_class = BaseYamlConfig

    def __init__(self, store_name: str, store_backend: Optional[dict]=None, overwrite_existing: bool=False, runtime_environment: Optional[dict]=None) -> None:
        import inspect
        __frame = inspect.currentframe()
        __file = __frame.f_code.co_filename
        __func = __frame.f_code.co_name
        for (k, v) in __frame.f_locals.items():
            if any(((var in k) for var in ('self', 'cls', '__frame', '__file', '__func'))):
                continue
            print(f'<INTROSPECT> {__file}:{__func}:{k} - {v.__class__.__name__}')
        if (not issubclass(self._configuration_class, BaseYamlConfig)):
            raise ge_exceptions.DataContextError('Invalid configuration: A configuration_class needs to inherit from the BaseYamlConfig class.')
        if (store_backend is not None):
            store_backend_module_name = store_backend.get('module_name', 'great_expectations.data_context.store')
            store_backend_class_name = store_backend.get('class_name', 'InMemoryStoreBackend')
            verify_dynamic_loading_support(module_name=store_backend_module_name)
            store_backend_class = load_class(store_backend_class_name, store_backend_module_name)
            if issubclass(store_backend_class, TupleStoreBackend):
                store_backend['filepath_suffix'] = store_backend.get('filepath_suffix', '.yml')
        super().__init__(store_backend=store_backend, runtime_environment=runtime_environment, store_name=store_name)
        self._config = {'store_name': store_name, 'store_backend': store_backend, 'overwrite_existing': overwrite_existing, 'runtime_environment': runtime_environment, 'module_name': self.__class__.__module__, 'class_name': self.__class__.__name__}
        filter_properties_dict(properties=self._config, clean_falsy=True, inplace=True)
        self._overwrite_existing = overwrite_existing

    def remove_key(self, key):
        import inspect
        __frame = inspect.currentframe()
        __file = __frame.f_code.co_filename
        __func = __frame.f_code.co_name
        for (k, v) in __frame.f_locals.items():
            if any(((var in k) for var in ('self', 'cls', '__frame', '__file', '__func'))):
                continue
            print(f'<INTROSPECT> {__file}:{__func}:{k} - {v.__class__.__name__}')
        return self.store_backend.remove_key(key)

    def serialize(self, key, value):
        import inspect
        __frame = inspect.currentframe()
        __file = __frame.f_code.co_filename
        __func = __frame.f_code.co_name
        for (k, v) in __frame.f_locals.items():
            if any(((var in k) for var in ('self', 'cls', '__frame', '__file', '__func'))):
                continue
            print(f'<INTROSPECT> {__file}:{__func}:{k} - {v.__class__.__name__}')
        if self.ge_cloud_mode:
            config_schema = value.get_schema_class()()
            return config_schema.dump(value)
        return value.to_yaml_str()

    def deserialize(self, key, value):
        import inspect
        __frame = inspect.currentframe()
        __file = __frame.f_code.co_filename
        __func = __frame.f_code.co_name
        for (k, v) in __frame.f_locals.items():
            if any(((var in k) for var in ('self', 'cls', '__frame', '__file', '__func'))):
                continue
            print(f'<INTROSPECT> {__file}:{__func}:{k} - {v.__class__.__name__}')
        config = value
        if isinstance(value, str):
            config: CommentedMap = yaml.load(value)
        try:
            return self._configuration_class.from_commented_map(commented_map=config)
        except ge_exceptions.InvalidBaseYamlConfigError:
            raise

    @property
    def overwrite_existing(self) -> bool:
        import inspect
        __frame = inspect.currentframe()
        __file = __frame.f_code.co_filename
        __func = __frame.f_code.co_name
        for (k, v) in __frame.f_locals.items():
            if any(((var in k) for var in ('self', 'cls', '__frame', '__file', '__func'))):
                continue
            print(f'<INTROSPECT> {__file}:{__func}:{k} - {v.__class__.__name__}')
        return self._overwrite_existing

    @overwrite_existing.setter
    def overwrite_existing(self, overwrite_existing: bool) -> None:
        import inspect
        __frame = inspect.currentframe()
        __file = __frame.f_code.co_filename
        __func = __frame.f_code.co_name
        for (k, v) in __frame.f_locals.items():
            if any(((var in k) for var in ('self', 'cls', '__frame', '__file', '__func'))):
                continue
            print(f'<INTROSPECT> {__file}:{__func}:{k} - {v.__class__.__name__}')
        self._overwrite_existing = overwrite_existing

    @property
    def config(self) -> dict:
        import inspect
        __frame = inspect.currentframe()
        __file = __frame.f_code.co_filename
        __func = __frame.f_code.co_name
        for (k, v) in __frame.f_locals.items():
            if any(((var in k) for var in ('self', 'cls', '__frame', '__file', '__func'))):
                continue
            print(f'<INTROSPECT> {__file}:{__func}:{k} - {v.__class__.__name__}')
        return self._config

    def self_check(self, pretty_print: bool=True) -> dict:
        import inspect
        __frame = inspect.currentframe()
        __file = __frame.f_code.co_filename
        __func = __frame.f_code.co_name
        for (k, v) in __frame.f_locals.items():
            if any(((var in k) for var in ('self', 'cls', '__frame', '__file', '__func'))):
                continue
            print(f'<INTROSPECT> {__file}:{__func}:{k} - {v.__class__.__name__}')
        report_object: dict = {'config': self.config}
        if pretty_print:
            print('Checking for existing keys...')
        report_object['keys'] = sorted((key.configuration_key for key in self.list_keys()))
        report_object['len_keys'] = len(report_object['keys'])
        len_keys: int = report_object['len_keys']
        if pretty_print:
            if (report_object['len_keys'] == 0):
                print(f'	{len_keys} keys found')
            else:
                print(f'	{len_keys} keys found:')
                for key in report_object['keys'][:10]:
                    print(f'		{str(key)}')
            if (len_keys > 10):
                print('\t\t...')
            print()
        self.serialization_self_check(pretty_print=pretty_print)
        return report_object

    def serialization_self_check(self, pretty_print: bool) -> None:
        import inspect
        __frame = inspect.currentframe()
        __file = __frame.f_code.co_filename
        __func = __frame.f_code.co_name
        for (k, v) in __frame.f_locals.items():
            if any(((var in k) for var in ('self', 'cls', '__frame', '__file', '__func'))):
                continue
            print(f'<INTROSPECT> {__file}:{__func}:{k} - {v.__class__.__name__}')
        raise NotImplementedError

    @staticmethod
    def determine_key(name: Optional[str], ge_cloud_id: Optional[str]) -> Union[(GeCloudIdentifier, ConfigurationIdentifier)]:
        import inspect
        __frame = inspect.currentframe()
        __file = __frame.f_code.co_filename
        __func = __frame.f_code.co_name
        for (k, v) in __frame.f_locals.items():
            if any(((var in k) for var in ('self', 'cls', '__frame', '__file', '__func'))):
                continue
            print(f'<INTROSPECT> {__file}:{__func}:{k} - {v.__class__.__name__}')
        assert (bool(name) ^ bool(ge_cloud_id)), 'Must provide either name or ge_cloud_id.'
        key: Union[(GeCloudIdentifier, ConfigurationIdentifier)]
        if ge_cloud_id:
            key = GeCloudIdentifier(resource_type='contract', ge_cloud_id=ge_cloud_id)
        else:
            key = ConfigurationIdentifier(configuration_key=name)
        return key
