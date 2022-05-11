
from great_expectations.render.renderer.content_block.content_block import ContentBlockRenderer
from great_expectations.render.types import RenderedStringTemplateContent

class ExpectationStringRenderer(ContentBlockRenderer):

    @classmethod
    def _missing_content_block_fn(cls, configuration=None, result=None, language=None, runtime_configuration=None, **kwargs):
        import inspect
        __frame = inspect.currentframe()
        __file = __frame.f_code.co_filename
        __func = __frame.f_code.co_name
        for (k, v) in __frame.f_locals.items():
            if any(((var in k) for var in ('self', 'cls', '__frame', '__file', '__func'))):
                continue
            print(f'<INTROSPECT> {__file}:{__func}:{k} - {v.__class__.__name__}')
        return [RenderedStringTemplateContent(**{'content_block_type': 'string_template', 'styling': {'parent': {'classes': ['alert', 'alert-warning']}}, 'string_template': {'template': '$expectation_type(**$kwargs)', 'params': {'expectation_type': configuration.expectation_type, 'kwargs': configuration.kwargs}, 'styling': {'params': {'expectation_type': {'classes': ['badge', 'badge-warning']}}}}})]

    @classmethod
    def _diagnostic_status_icon_renderer(cls, configuration=None, result=None, language=None, runtime_configuration=None, **kwargs):
        import inspect
        __frame = inspect.currentframe()
        __file = __frame.f_code.co_filename
        __func = __frame.f_code.co_name
        for (k, v) in __frame.f_locals.items():
            if any(((var in k) for var in ('self', 'cls', '__frame', '__file', '__func'))):
                continue
            print(f'<INTROSPECT> {__file}:{__func}:{k} - {v.__class__.__name__}')
        assert result, 'Must provide a result object.'
        if result.exception_info['raised_exception']:
            return RenderedStringTemplateContent(**{'content_block_type': 'string_template', 'string_template': {'template': '$icon', 'params': {'icon': '', 'markdown_status_icon': '❗'}, 'styling': {'params': {'icon': {'classes': ['fas', 'fa-exclamation-triangle', 'text-warning'], 'tag': 'i'}}}}})
        if result.success:
            return RenderedStringTemplateContent(**{'content_block_type': 'string_template', 'string_template': {'template': '$icon', 'params': {'icon': '', 'markdown_status_icon': '✅'}, 'styling': {'params': {'icon': {'classes': ['fas', 'fa-check-circle', 'text-success'], 'tag': 'i'}}}}, 'styling': {'parent': {'classes': ['hide-succeeded-validation-target-child']}}})
        else:
            return RenderedStringTemplateContent(**{'content_block_type': 'string_template', 'string_template': {'template': '$icon', 'params': {'icon': '', 'markdown_status_icon': '❌'}, 'styling': {'params': {'icon': {'tag': 'i', 'classes': ['fas', 'fa-times', 'text-danger']}}}}})
