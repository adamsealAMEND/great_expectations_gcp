
from typing import Any, Optional
from great_expectations.core.usage_statistics.anonymizers.base import BaseAnonymizer
from great_expectations.data_context.store.store import Store

class StoreAnonymizer(BaseAnonymizer):

    def __init__(self, aggregate_anonymizer: 'Anonymizer', salt: Optional[str]=None) -> None:
        import inspect
        __frame = inspect.currentframe()
        __file = __frame.f_code.co_filename
        __func = __frame.f_code.co_name
        for (k, v) in __frame.f_locals.items():
            if any(((var in k) for var in ('self', 'cls', '__frame', '__file', '__func'))):
                continue
            print(f'<INTROSPECT> {__file}:{__func}:{k} - {v.__class__.__name__}')
        super().__init__(salt=salt)
        self._aggregate_anonymizer = aggregate_anonymizer

    def anonymize(self, store_name: str, store_obj: Store, obj: Optional[object]=None) -> Any:
        import inspect
        __frame = inspect.currentframe()
        __file = __frame.f_code.co_filename
        __func = __frame.f_code.co_name
        for (k, v) in __frame.f_locals.items():
            if any(((var in k) for var in ('self', 'cls', '__frame', '__file', '__func'))):
                continue
            print(f'<INTROSPECT> {__file}:{__func}:{k} - {v.__class__.__name__}')
        anonymized_info_dict = {}
        anonymized_info_dict['anonymized_name'] = self._anonymize_string(store_name)
        store_backend_obj = store_obj.store_backend
        self._anonymize_object_info(object_=store_obj, anonymized_info_dict=anonymized_info_dict)
        anonymized_info_dict['anonymized_store_backend'] = self._anonymize_store_backend_info(store_backend_obj=store_backend_obj)
        return anonymized_info_dict

    def _anonymize_store_backend_info(self, store_backend_obj: Optional[object]=None, store_backend_object_config: Optional[dict]=None) -> dict:
        import inspect
        __frame = inspect.currentframe()
        __file = __frame.f_code.co_filename
        __func = __frame.f_code.co_name
        for (k, v) in __frame.f_locals.items():
            if any(((var in k) for var in ('self', 'cls', '__frame', '__file', '__func'))):
                continue
            print(f'<INTROSPECT> {__file}:{__func}:{k} - {v.__class__.__name__}')
        assert (store_backend_obj or store_backend_object_config), 'Must pass store_backend_obj or store_backend_object_config.'
        anonymized_info_dict = {}
        if (store_backend_obj is not None):
            self._anonymize_object_info(object_=store_backend_obj, anonymized_info_dict=anonymized_info_dict)
        else:
            class_name = store_backend_object_config.get('class_name')
            module_name = store_backend_object_config.get('module_name')
            if (module_name is None):
                module_name = 'great_expectations.data_context.store'
            self._anonymize_object_info(object_config={'class_name': class_name, 'module_name': module_name}, anonymized_info_dict=anonymized_info_dict)
        return anonymized_info_dict

    def can_handle(self, obj: Optional[object]=None, **kwargs) -> bool:
        import inspect
        __frame = inspect.currentframe()
        __file = __frame.f_code.co_filename
        __func = __frame.f_code.co_name
        for (k, v) in __frame.f_locals.items():
            if any(((var in k) for var in ('self', 'cls', '__frame', '__file', '__func'))):
                continue
            print(f'<INTROSPECT> {__file}:{__func}:{k} - {v.__class__.__name__}')
        from great_expectations.data_context.store.store import Store
        return (((obj is not None) and isinstance(obj, Store)) or (('store_name' in kwargs) or ('store_obj' in kwargs)))
