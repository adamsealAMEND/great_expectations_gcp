
import logging
import os
import traceback
from collections import OrderedDict
from typing import Any, List, Optional, Tuple
import great_expectations.exceptions as exceptions
from great_expectations.core import ExpectationSuite
from great_expectations.core.util import nested_update
from great_expectations.data_context.store.html_site_store import HtmlSiteStore, SiteSectionIdentifier
from great_expectations.data_context.store.json_site_store import JsonSiteStore
from great_expectations.data_context.types.resource_identifiers import ExpectationSuiteIdentifier, GeCloudIdentifier, ValidationResultIdentifier
from great_expectations.data_context.util import instantiate_class_from_config
from great_expectations.render.util import resource_key_passes_run_name_filter
logger = logging.getLogger(__name__)
FALSEY_YAML_STRINGS = ['0', 'None', 'False', 'false', 'FALSE', 'none', 'NONE']

class SiteBuilder():
    "SiteBuilder builds data documentation for the project defined by a\n    DataContext.\n\n    A data documentation site consists of HTML pages for expectation suites,\n    profiling and validation results, and\n    an index.html page that links to all the pages.\n\n    The exact behavior of SiteBuilder is controlled by configuration in the\n    DataContext's great_expectations.yml file.\n\n    Users can specify:\n\n        * which datasources to document (by default, all)\n        * whether to include expectations, validations and profiling results\n        sections (by default, all)\n        * where the expectations and validations should be read from\n        (filesystem or S3)\n        * where the HTML files should be written (filesystem or S3)\n        * which renderer and view class should be used to render each section\n\n    Here is an example of a minimal configuration for a site::\n\n        local_site:\n            class_name: SiteBuilder\n            store_backend:\n                class_name: TupleS3StoreBackend\n                bucket: data_docs.my_company.com\n                prefix: /data_docs/\n\n\n    A more verbose configuration can also control individual sections and\n    override renderers, views, and stores::\n\n        local_site:\n            class_name: SiteBuilder\n            store_backend:\n                class_name: TupleS3StoreBackend\n                bucket: data_docs.my_company.com\n                prefix: /data_docs/\n            site_index_builder:\n                class_name: DefaultSiteIndexBuilder\n\n            # Verbose version:\n            # site_index_builder:\n            #     module_name: great_expectations.render.builder\n            #     class_name: DefaultSiteIndexBuilder\n            #     renderer:\n            #         module_name: great_expectations.render.renderer\n            #         class_name: SiteIndexPageRenderer\n            #     view:\n            #         module_name: great_expectations.render.view\n            #         class_name: DefaultJinjaIndexPageView\n\n            site_section_builders:\n                # Minimal specification\n                expectations:\n                    class_name: DefaultSiteSectionBuilder\n                    source_store_name: expectation_store\n                renderer:\n                    module_name: great_expectations.render.renderer\n                    class_name: ExpectationSuitePageRenderer\n\n                # More verbose specification with optional arguments\n                validations:\n                    module_name: great_expectations.data_context.render\n                    class_name: DefaultSiteSectionBuilder\n                    source_store_name: local_validation_store\n                    renderer:\n                        module_name: great_expectations.render.renderer\n                        class_name: SiteIndexPageRenderer\n                    view:\n                        module_name: great_expectations.render.view\n                        class_name: DefaultJinjaIndexPageView\n    "

    def __init__(self, data_context, store_backend, site_name=None, site_index_builder=None, show_how_to_buttons=True, site_section_builders=None, runtime_environment=None, ge_cloud_mode=False, **kwargs) -> None:
        import inspect
        __frame = inspect.currentframe()
        __file = __frame.f_code.co_filename
        __func = __frame.f_code.co_name
        for (k, v) in __frame.f_locals.items():
            if any(((var in k) for var in ('self', 'cls', '__frame', '__file', '__func'))):
                continue
            print(f'<INTROSPECT> {__file}:{__func}:{k} - {v.__class__.__name__}')
        self.site_name = site_name
        self.data_context = data_context
        self.store_backend = store_backend
        self.show_how_to_buttons = show_how_to_buttons
        self.ge_cloud_mode = ge_cloud_mode
        usage_statistics_config = data_context.anonymous_usage_statistics
        data_context_id = None
        if (usage_statistics_config and usage_statistics_config.enabled and usage_statistics_config.data_context_id):
            data_context_id = usage_statistics_config.data_context_id
        self.data_context_id = data_context_id
        custom_styles_directory = None
        plugins_directory = data_context.plugins_directory
        if (plugins_directory and os.path.isdir(os.path.join(plugins_directory, 'custom_data_docs', 'styles'))):
            custom_styles_directory = os.path.join(plugins_directory, 'custom_data_docs', 'styles')
        custom_views_directory = None
        if (plugins_directory and os.path.isdir(os.path.join(plugins_directory, 'custom_data_docs', 'views'))):
            custom_views_directory = os.path.join(plugins_directory, 'custom_data_docs', 'views')
        if (site_index_builder is None):
            site_index_builder = {'class_name': 'DefaultSiteIndexBuilder'}
        if ge_cloud_mode:
            self.target_store = JsonSiteStore(store_backend=store_backend, runtime_environment=runtime_environment)
        else:
            self.target_store = HtmlSiteStore(store_backend=store_backend, runtime_environment=runtime_environment)
        default_site_section_builders_config = {'expectations': {'class_name': 'DefaultSiteSectionBuilder', 'source_store_name': data_context.expectations_store_name, 'renderer': {'class_name': 'ExpectationSuitePageRenderer'}}, 'validations': {'class_name': 'DefaultSiteSectionBuilder', 'source_store_name': data_context.validations_store_name, 'renderer': {'class_name': 'ValidationResultsPageRenderer'}, 'validation_results_limit': site_index_builder.get('validation_results_limit')}, 'profiling': {'class_name': 'DefaultSiteSectionBuilder', 'source_store_name': data_context.validations_store_name, 'renderer': {'class_name': 'ProfilingResultsPageRenderer'}}}
        if (site_section_builders is None):
            site_section_builders = default_site_section_builders_config
        else:
            site_section_builders = nested_update(default_site_section_builders_config, site_section_builders)
        if (site_section_builders.get('validations', 'None') not in FALSEY_YAML_STRINGS):
            if (site_section_builders['validations'].get('run_name_filter') is None):
                site_section_builders['validations']['run_name_filter'] = {'not_includes': 'profiling'}
        if (site_section_builders.get('profiling', 'None') not in FALSEY_YAML_STRINGS):
            if (site_section_builders['profiling'].get('run_name_filter') is None):
                site_section_builders['profiling']['run_name_filter'] = {'includes': 'profiling'}
        self.site_section_builders = {}
        for (site_section_name, site_section_config) in site_section_builders.items():
            if ((not site_section_config) or (site_section_config in FALSEY_YAML_STRINGS)):
                continue
            module_name = (site_section_config.get('module_name') or 'great_expectations.render.renderer.site_builder')
            self.site_section_builders[site_section_name] = instantiate_class_from_config(config=site_section_config, runtime_environment={'data_context': data_context, 'target_store': self.target_store, 'custom_styles_directory': custom_styles_directory, 'custom_views_directory': custom_views_directory, 'data_context_id': self.data_context_id, 'show_how_to_buttons': self.show_how_to_buttons, 'ge_cloud_mode': self.ge_cloud_mode}, config_defaults={'name': site_section_name, 'module_name': module_name})
            if (not self.site_section_builders[site_section_name]):
                raise exceptions.ClassInstantiationError(module_name=module_name, package_name=None, class_name=site_section_config['class_name'])
        module_name = (site_index_builder.get('module_name') or 'great_expectations.render.renderer.site_builder')
        class_name = (site_index_builder.get('class_name') or 'DefaultSiteIndexBuilder')
        self.site_index_builder = instantiate_class_from_config(config=site_index_builder, runtime_environment={'data_context': data_context, 'custom_styles_directory': custom_styles_directory, 'custom_views_directory': custom_views_directory, 'show_how_to_buttons': self.show_how_to_buttons, 'target_store': self.target_store, 'site_name': self.site_name, 'data_context_id': self.data_context_id, 'source_stores': {section_name: section_config.get('source_store_name') for (section_name, section_config) in site_section_builders.items() if (section_config not in FALSEY_YAML_STRINGS)}, 'site_section_builders_config': site_section_builders, 'ge_cloud_mode': self.ge_cloud_mode}, config_defaults={'name': 'site_index_builder', 'module_name': module_name, 'class_name': class_name})
        if (not self.site_index_builder):
            raise exceptions.ClassInstantiationError(module_name=module_name, package_name=None, class_name=site_index_builder['class_name'])

    def clean_site(self) -> None:
        import inspect
        __frame = inspect.currentframe()
        __file = __frame.f_code.co_filename
        __func = __frame.f_code.co_name
        for (k, v) in __frame.f_locals.items():
            if any(((var in k) for var in ('self', 'cls', '__frame', '__file', '__func'))):
                continue
            print(f'<INTROSPECT> {__file}:{__func}:{k} - {v.__class__.__name__}')
        self.target_store.clean_site()

    def build(self, resource_identifiers=None, build_index: bool=True):
        import inspect
        __frame = inspect.currentframe()
        __file = __frame.f_code.co_filename
        __func = __frame.f_code.co_name
        for (k, v) in __frame.f_locals.items():
            if any(((var in k) for var in ('self', 'cls', '__frame', '__file', '__func'))):
                continue
            print(f'<INTROSPECT> {__file}:{__func}:{k} - {v.__class__.__name__}')
        '\n\n        :param resource_identifiers: a list of resource identifiers\n        (ExpectationSuiteIdentifier,\n                            ValidationResultIdentifier). If specified,\n                            rebuild HTML(or other views the data docs\n                            site renders) only for the resources in this list.\n                            This supports incremental build of data docs sites\n                            (e.g., when a new validation result is created)\n                            and avoids full rebuild.\n\n        :param build_index: a flag if False, skips building the index page\n\n        :return:\n        '
        for site_section_builder in self.site_section_builders.values():
            site_section_builder.build(resource_identifiers=resource_identifiers)
        if self.ge_cloud_mode:
            return
        self.target_store.copy_static_assets()
        (_, index_links_dict) = self.site_index_builder.build(build_index=build_index)
        return (self.get_resource_url(only_if_exists=False), index_links_dict)

    def get_resource_url(self, resource_identifier=None, only_if_exists=True):
        import inspect
        __frame = inspect.currentframe()
        __file = __frame.f_code.co_filename
        __func = __frame.f_code.co_name
        for (k, v) in __frame.f_locals.items():
            if any(((var in k) for var in ('self', 'cls', '__frame', '__file', '__func'))):
                continue
            print(f'<INTROSPECT> {__file}:{__func}:{k} - {v.__class__.__name__}')
        "\n        Return the URL of the HTML document that renders a resource\n        (e.g., an expectation suite or a validation result).\n\n        :param resource_identifier: ExpectationSuiteIdentifier,\n        ValidationResultIdentifier or any other type's identifier. The\n        argument is optional - when not supplied, the method returns the URL of\n        the index page.\n        :return: URL (string)\n        "
        return self.target_store.get_url_for_resource(resource_identifier=resource_identifier, only_if_exists=only_if_exists)

class DefaultSiteSectionBuilder():

    def __init__(self, name, data_context, target_store, source_store_name, custom_styles_directory=None, custom_views_directory=None, show_how_to_buttons=True, run_name_filter=None, validation_results_limit=None, renderer=None, view=None, data_context_id=None, ge_cloud_mode=False, **kwargs) -> None:
        import inspect
        __frame = inspect.currentframe()
        __file = __frame.f_code.co_filename
        __func = __frame.f_code.co_name
        for (k, v) in __frame.f_locals.items():
            if any(((var in k) for var in ('self', 'cls', '__frame', '__file', '__func'))):
                continue
            print(f'<INTROSPECT> {__file}:{__func}:{k} - {v.__class__.__name__}')
        self.name = name
        self.data_context = data_context
        self.source_store = data_context.stores[source_store_name]
        self.target_store = target_store
        self.run_name_filter = run_name_filter
        self.validation_results_limit = validation_results_limit
        self.data_context_id = data_context_id
        self.show_how_to_buttons = show_how_to_buttons
        self.ge_cloud_mode = ge_cloud_mode
        if (renderer is None):
            raise exceptions.InvalidConfigError('SiteSectionBuilder requires a renderer configuration with a class_name key.')
        module_name = (renderer.get('module_name') or 'great_expectations.render.renderer')
        self.renderer_class = instantiate_class_from_config(config=renderer, runtime_environment={'data_context': data_context}, config_defaults={'module_name': module_name})
        if (not self.renderer_class):
            raise exceptions.ClassInstantiationError(module_name=module_name, package_name=None, class_name=renderer['class_name'])
        module_name = 'great_expectations.render.view'
        if (view is None):
            view = {'module_name': module_name, 'class_name': 'DefaultJinjaPageView'}
        module_name = (view.get('module_name') or module_name)
        self.view_class = instantiate_class_from_config(config=view, runtime_environment={'custom_styles_directory': custom_styles_directory, 'custom_views_directory': custom_views_directory}, config_defaults={'module_name': module_name})
        if (not self.view_class):
            raise exceptions.ClassInstantiationError(module_name=view['module_name'], package_name=None, class_name=view['class_name'])

    def build(self, resource_identifiers=None) -> None:
        import inspect
        __frame = inspect.currentframe()
        __file = __frame.f_code.co_filename
        __func = __frame.f_code.co_name
        for (k, v) in __frame.f_locals.items():
            if any(((var in k) for var in ('self', 'cls', '__frame', '__file', '__func'))):
                continue
            print(f'<INTROSPECT> {__file}:{__func}:{k} - {v.__class__.__name__}')
        source_store_keys = self.source_store.list_keys()
        if ((self.name == 'validations') and self.validation_results_limit):
            source_store_keys = sorted(source_store_keys, key=(lambda x: x.run_id.run_time), reverse=True)[:self.validation_results_limit]
        for resource_key in source_store_keys:
            if (resource_identifiers and (resource_key not in resource_identifiers)):
                continue
            if (self.run_name_filter and (not isinstance(resource_key, GeCloudIdentifier))):
                if (not resource_key_passes_run_name_filter(resource_key, self.run_name_filter)):
                    continue
            try:
                resource = self.source_store.get(resource_key)
                if isinstance(resource_key, ExpectationSuiteIdentifier):
                    resource = ExpectationSuite(**resource, data_context=self.data_context)
            except exceptions.InvalidKeyError:
                logger.warning(f'Object with Key: {str(resource_key)} could not be retrieved. Skipping...')
                continue
            if isinstance(resource_key, ExpectationSuiteIdentifier):
                expectation_suite_name = resource_key.expectation_suite_name
                logger.debug(f'        Rendering expectation suite {expectation_suite_name}')
            elif isinstance(resource_key, ValidationResultIdentifier):
                run_id = resource_key.run_id
                run_name = run_id.run_name
                run_time = run_id.run_time
                expectation_suite_name = resource_key.expectation_suite_identifier.expectation_suite_name
                if (self.name == 'profiling'):
                    logger.debug(f'        Rendering profiling for batch {resource_key.batch_identifier}')
                else:
                    logger.debug(f'        Rendering validation: run name: {run_name}, run time: {run_time}, suite {expectation_suite_name} for batch {resource_key.batch_identifier}')
            try:
                rendered_content = self.renderer_class.render(resource)
                if self.ge_cloud_mode:
                    self.target_store.set(GeCloudIdentifier(resource_type='rendered_data_doc'), rendered_content, source_type=resource_key.resource_type, source_id=resource_key.ge_cloud_id)
                else:
                    viewable_content = self.view_class.render(rendered_content, data_context_id=self.data_context_id, show_how_to_buttons=self.show_how_to_buttons)
                    self.target_store.set(SiteSectionIdentifier(site_section_name=self.name, resource_identifier=resource_key), viewable_content)
            except Exception as e:
                exception_message = 'An unexpected Exception occurred during data docs rendering.  Because of this error, certain parts of data docs will not be rendered properly and/or may not appear altogether.  Please use the trace, included in this message, to diagnose and repair the underlying issue.  Detailed information follows:\n                '
                exception_traceback = traceback.format_exc()
                exception_message += f'{type(e).__name__}: "{str(e)}".  Traceback: "{exception_traceback}".'
                logger.error(exception_message)

class DefaultSiteIndexBuilder():

    def __init__(self, name, site_name, data_context, target_store, site_section_builders_config, custom_styles_directory=None, custom_views_directory=None, show_how_to_buttons=True, validation_results_limit=None, renderer=None, view=None, data_context_id=None, source_stores=None, **kwargs) -> None:
        import inspect
        __frame = inspect.currentframe()
        __file = __frame.f_code.co_filename
        __func = __frame.f_code.co_name
        for (k, v) in __frame.f_locals.items():
            if any(((var in k) for var in ('self', 'cls', '__frame', '__file', '__func'))):
                continue
            print(f'<INTROSPECT> {__file}:{__func}:{k} - {v.__class__.__name__}')
        self.name = name
        self.site_name = site_name
        self.data_context = data_context
        self.target_store = target_store
        self.validation_results_limit = validation_results_limit
        self.data_context_id = data_context_id
        self.show_how_to_buttons = show_how_to_buttons
        self.source_stores = (source_stores or {})
        self.site_section_builders_config = (site_section_builders_config or {})
        if (renderer is None):
            renderer = {'module_name': 'great_expectations.render.renderer', 'class_name': 'SiteIndexPageRenderer'}
        module_name = (renderer.get('module_name') or 'great_expectations.render.renderer')
        self.renderer_class = instantiate_class_from_config(config=renderer, runtime_environment={'data_context': data_context}, config_defaults={'module_name': module_name})
        if (not self.renderer_class):
            raise exceptions.ClassInstantiationError(module_name=module_name, package_name=None, class_name=renderer['class_name'])
        module_name = 'great_expectations.render.view'
        if (view is None):
            view = {'module_name': module_name, 'class_name': 'DefaultJinjaIndexPageView'}
        module_name = (view.get('module_name') or module_name)
        self.view_class = instantiate_class_from_config(config=view, runtime_environment={'custom_styles_directory': custom_styles_directory, 'custom_views_directory': custom_views_directory}, config_defaults={'module_name': module_name})
        if (not self.view_class):
            raise exceptions.ClassInstantiationError(module_name=view['module_name'], package_name=None, class_name=view['class_name'])

    def add_resource_info_to_index_links_dict(self, index_links_dict, expectation_suite_name, section_name, batch_identifier=None, run_id=None, validation_success=None, run_time=None, run_name=None, asset_name=None, batch_kwargs=None, batch_spec=None):
        import inspect
        __frame = inspect.currentframe()
        __file = __frame.f_code.co_filename
        __func = __frame.f_code.co_name
        for (k, v) in __frame.f_locals.items():
            if any(((var in k) for var in ('self', 'cls', '__frame', '__file', '__func'))):
                continue
            print(f'<INTROSPECT> {__file}:{__func}:{k} - {v.__class__.__name__}')
        import os
        if (f'{section_name}_links' not in index_links_dict):
            index_links_dict[f'{section_name}_links'] = []
        if run_id:
            filepath = (os.path.join('validations', *expectation_suite_name.split('.'), *run_id.to_tuple(), batch_identifier) + '.html')
        else:
            filepath = (os.path.join('expectations', *expectation_suite_name.split('.')) + '.html')
        expectation_suite_filepath = os.path.join('expectations', *expectation_suite_name.split('.'))
        expectation_suite_filepath += '.html'
        index_links_dict[f'{section_name}_links'].append({'expectation_suite_name': expectation_suite_name, 'filepath': filepath, 'run_id': run_id, 'batch_identifier': batch_identifier, 'validation_success': validation_success, 'run_time': run_time, 'run_name': run_name, 'asset_name': asset_name, 'batch_kwargs': batch_kwargs, 'batch_spec': batch_spec, 'expectation_suite_filepath': (expectation_suite_filepath if run_id else None)})
        return index_links_dict

    def get_calls_to_action(self):
        import inspect
        __frame = inspect.currentframe()
        __file = __frame.f_code.co_filename
        __func = __frame.f_code.co_name
        for (k, v) in __frame.f_locals.items():
            if any(((var in k) for var in ('self', 'cls', '__frame', '__file', '__func'))):
                continue
            print(f'<INTROSPECT> {__file}:{__func}:{k} - {v.__class__.__name__}')
        usage_statistics = None
        return {'header': 'To continue exploring Great Expectations check out one of these tutorials...', 'buttons': self._get_call_to_action_buttons(usage_statistics)}

    def _get_call_to_action_buttons(self, usage_statistics):
        import inspect
        __frame = inspect.currentframe()
        __file = __frame.f_code.co_filename
        __func = __frame.f_code.co_name
        for (k, v) in __frame.f_locals.items():
            if any(((var in k) for var in ('self', 'cls', '__frame', '__file', '__func'))):
                continue
            print(f'<INTROSPECT> {__file}:{__func}:{k} - {v.__class__.__name__}')
        '\n        Build project and user specific calls to action buttons.\n\n        This can become progressively smarter about project and user specific\n        calls to action.\n        '
        create_expectations = CallToActionButton('How to Create Expectations', 'https://docs.greatexpectations.io/docs/guides/expectations/how_to_create_and_edit_expectations_with_instant_feedback_from_a_sample_batch_of_data')
        see_glossary = CallToActionButton('See More Kinds of Expectations', 'https://greatexpectations.io/expectations')
        validation_playground = CallToActionButton('How to Validate Data', 'https://docs.greatexpectations.io/docs/guides/validation/checkpoints/how_to_create_a_new_checkpoint')
        customize_data_docs = CallToActionButton('How to Customize Data Docs', 'https://docs.greatexpectations.io/docs/reference/data_docs#customizing-html-documentation')
        team_site = CallToActionButton('How to Set Up a Team Site', 'https://docs.greatexpectations.io/docs/guides/setup/configuring_data_docs/how_to_host_and_share_data_docs_on_a_filesystem')
        results = []
        results.append(create_expectations)
        results.append(validation_playground)
        results.append(team_site)
        if usage_statistics:
            for button in results:
                button.link = (button.link + usage_statistics)
        return results

    def build(self, skip_and_clean_missing=True, build_index: bool=True) -> Tuple[(Any, Optional[OrderedDict])]:
        import inspect
        __frame = inspect.currentframe()
        __file = __frame.f_code.co_filename
        __func = __frame.f_code.co_name
        for (k, v) in __frame.f_locals.items():
            if any(((var in k) for var in ('self', 'cls', '__frame', '__file', '__func'))):
                continue
            print(f'<INTROSPECT> {__file}:{__func}:{k} - {v.__class__.__name__}')
        '\n        :param skip_and_clean_missing: if True, target html store keys without corresponding source store keys will\n        be skipped and removed from the target store\n        :param build_index: a flag if False, skips building the index page\n        :return: tuple(index_page_url, index_links_dict)\n        '
        logger.debug('DefaultSiteIndexBuilder.build')
        if (not build_index):
            logger.debug('Skipping index rendering')
            return (None, None)
        index_links_dict = OrderedDict()
        index_links_dict['site_name'] = self.site_name
        if self.show_how_to_buttons:
            index_links_dict['cta_object'] = self.get_calls_to_action()
        self._add_expectations_to_index_links(index_links_dict, skip_and_clean_missing)
        validation_and_profiling_result_site_keys = self._build_validation_and_profiling_result_site_keys(skip_and_clean_missing)
        self._add_profiling_to_index_links(index_links_dict, validation_and_profiling_result_site_keys)
        self._add_validations_to_index_links(index_links_dict, validation_and_profiling_result_site_keys)
        viewable_content = ''
        try:
            rendered_content = self.renderer_class.render(index_links_dict)
            viewable_content = self.view_class.render(rendered_content, data_context_id=self.data_context_id, show_how_to_buttons=self.show_how_to_buttons)
        except Exception as e:
            exception_message = 'An unexpected Exception occurred during data docs rendering.  Because of this error, certain parts of data docs will not be rendered properly and/or may not appear altogether.  Please use the trace, included in this message, to diagnose and repair the underlying issue.  Detailed information follows:\n            '
            exception_traceback = traceback.format_exc()
            exception_message += f'{type(e).__name__}: "{str(e)}".  Traceback: "{exception_traceback}".'
            logger.error(exception_message)
        return (self.target_store.write_index_page(viewable_content), index_links_dict)

    def _add_expectations_to_index_links(self, index_links_dict: OrderedDict, skip_and_clean_missing: bool) -> None:
        import inspect
        __frame = inspect.currentframe()
        __file = __frame.f_code.co_filename
        __func = __frame.f_code.co_name
        for (k, v) in __frame.f_locals.items():
            if any(((var in k) for var in ('self', 'cls', '__frame', '__file', '__func'))):
                continue
            print(f'<INTROSPECT> {__file}:{__func}:{k} - {v.__class__.__name__}')
        expectations = self.site_section_builders_config.get('expectations', 'None')
        if (expectations and (expectations not in FALSEY_YAML_STRINGS)):
            expectation_suite_source_keys = self.data_context.stores[self.site_section_builders_config['expectations'].get('source_store_name')].list_keys()
            expectation_suite_site_keys = [ExpectationSuiteIdentifier.from_tuple(expectation_suite_tuple) for expectation_suite_tuple in self.target_store.store_backends[ExpectationSuiteIdentifier].list_keys()]
            if skip_and_clean_missing:
                cleaned_keys = []
                for expectation_suite_site_key in expectation_suite_site_keys:
                    if (expectation_suite_site_key not in expectation_suite_source_keys):
                        self.target_store.store_backends[ExpectationSuiteIdentifier].remove_key(expectation_suite_site_key)
                    else:
                        cleaned_keys.append(expectation_suite_site_key)
                expectation_suite_site_keys = cleaned_keys
            for expectation_suite_key in expectation_suite_site_keys:
                self.add_resource_info_to_index_links_dict(index_links_dict=index_links_dict, expectation_suite_name=expectation_suite_key.expectation_suite_name, section_name='expectations')

    def _build_validation_and_profiling_result_site_keys(self, skip_and_clean_missing: bool) -> List[ValidationResultIdentifier]:
        import inspect
        __frame = inspect.currentframe()
        __file = __frame.f_code.co_filename
        __func = __frame.f_code.co_name
        for (k, v) in __frame.f_locals.items():
            if any(((var in k) for var in ('self', 'cls', '__frame', '__file', '__func'))):
                continue
            print(f'<INTROSPECT> {__file}:{__func}:{k} - {v.__class__.__name__}')
        validation_and_profiling_result_site_keys = []
        validations = self.site_section_builders_config.get('validations', 'None')
        profiling = self.site_section_builders_config.get('profiling', 'None')
        if ((validations and (validations not in FALSEY_YAML_STRINGS)) or (profiling and (profiling not in FALSEY_YAML_STRINGS))):
            source_store = ('validations' if (validations and (validations not in FALSEY_YAML_STRINGS)) else 'profiling')
            validation_and_profiling_result_source_keys = self.data_context.stores[self.site_section_builders_config[source_store].get('source_store_name')].list_keys()
            validation_and_profiling_result_site_keys = [ValidationResultIdentifier.from_tuple(validation_result_tuple) for validation_result_tuple in self.target_store.store_backends[ValidationResultIdentifier].list_keys()]
            if skip_and_clean_missing:
                cleaned_keys = []
                for validation_result_site_key in validation_and_profiling_result_site_keys:
                    if (validation_result_site_key not in validation_and_profiling_result_source_keys):
                        self.target_store.store_backends[ValidationResultIdentifier].remove_key(validation_result_site_key)
                    else:
                        cleaned_keys.append(validation_result_site_key)
                validation_and_profiling_result_site_keys = cleaned_keys
        return validation_and_profiling_result_site_keys

    def _add_profiling_to_index_links(self, index_links_dict: OrderedDict, validation_and_profiling_result_site_keys: List[ValidationResultIdentifier]) -> None:
        import inspect
        __frame = inspect.currentframe()
        __file = __frame.f_code.co_filename
        __func = __frame.f_code.co_name
        for (k, v) in __frame.f_locals.items():
            if any(((var in k) for var in ('self', 'cls', '__frame', '__file', '__func'))):
                continue
            print(f'<INTROSPECT> {__file}:{__func}:{k} - {v.__class__.__name__}')
        profiling = self.site_section_builders_config.get('profiling', 'None')
        if (profiling and (profiling not in FALSEY_YAML_STRINGS)):
            profiling_run_name_filter = self.site_section_builders_config['profiling']['run_name_filter']
            profiling_result_site_keys = [validation_result_key for validation_result_key in validation_and_profiling_result_site_keys if resource_key_passes_run_name_filter(validation_result_key, profiling_run_name_filter)]
            for profiling_result_key in profiling_result_site_keys:
                try:
                    validation = self.data_context.get_validation_result(batch_identifier=profiling_result_key.batch_identifier, expectation_suite_name=profiling_result_key.expectation_suite_identifier.expectation_suite_name, run_id=profiling_result_key.run_id, validations_store_name=self.source_stores.get('profiling'))
                    batch_kwargs = validation.meta.get('batch_kwargs', {})
                    batch_spec = validation.meta.get('batch_spec', {})
                    self.add_resource_info_to_index_links_dict(index_links_dict=index_links_dict, expectation_suite_name=profiling_result_key.expectation_suite_identifier.expectation_suite_name, section_name='profiling', batch_identifier=profiling_result_key.batch_identifier, run_id=profiling_result_key.run_id, run_time=profiling_result_key.run_id.run_time, run_name=profiling_result_key.run_id.run_name, asset_name=(batch_kwargs.get('data_asset_name') or batch_spec.get('data_asset_name')), batch_kwargs=batch_kwargs, batch_spec=batch_spec)
                except Exception:
                    error_msg = f'Profiling result not found: {str(profiling_result_key.to_tuple()):s} - skipping'
                    logger.warning(error_msg)

    def _add_validations_to_index_links(self, index_links_dict: OrderedDict, validation_and_profiling_result_site_keys: List[ValidationResultIdentifier]) -> None:
        import inspect
        __frame = inspect.currentframe()
        __file = __frame.f_code.co_filename
        __func = __frame.f_code.co_name
        for (k, v) in __frame.f_locals.items():
            if any(((var in k) for var in ('self', 'cls', '__frame', '__file', '__func'))):
                continue
            print(f'<INTROSPECT> {__file}:{__func}:{k} - {v.__class__.__name__}')
        validations = self.site_section_builders_config.get('validations', 'None')
        if (validations and (validations not in FALSEY_YAML_STRINGS)):
            validations_run_name_filter = self.site_section_builders_config['validations']['run_name_filter']
            validation_result_site_keys = [validation_result_key for validation_result_key in validation_and_profiling_result_site_keys if resource_key_passes_run_name_filter(validation_result_key, validations_run_name_filter)]
            validation_result_site_keys = sorted(validation_result_site_keys, key=(lambda x: x.run_id.run_time), reverse=True)
            if self.validation_results_limit:
                validation_result_site_keys = validation_result_site_keys[:self.validation_results_limit]
            for validation_result_key in validation_result_site_keys:
                try:
                    validation = self.data_context.get_validation_result(batch_identifier=validation_result_key.batch_identifier, expectation_suite_name=validation_result_key.expectation_suite_identifier.expectation_suite_name, run_id=validation_result_key.run_id, validations_store_name=self.source_stores.get('validations'))
                    validation_success = validation.success
                    batch_kwargs = validation.meta.get('batch_kwargs', {})
                    batch_spec = validation.meta.get('batch_spec', {})
                    self.add_resource_info_to_index_links_dict(index_links_dict=index_links_dict, expectation_suite_name=validation_result_key.expectation_suite_identifier.expectation_suite_name, section_name='validations', batch_identifier=validation_result_key.batch_identifier, run_id=validation_result_key.run_id, validation_success=validation_success, run_time=validation_result_key.run_id.run_time, run_name=validation_result_key.run_id.run_name, asset_name=(batch_kwargs.get('data_asset_name') or batch_spec.get('data_asset_name')), batch_kwargs=batch_kwargs, batch_spec=batch_spec)
                except Exception:
                    error_msg = f'Validation result not found: {str(validation_result_key.to_tuple()):s} - skipping'
                    logger.warning(error_msg)

class CallToActionButton():

    def __init__(self, title, link) -> None:
        import inspect
        __frame = inspect.currentframe()
        __file = __frame.f_code.co_filename
        __func = __frame.f_code.co_name
        for (k, v) in __frame.f_locals.items():
            if any(((var in k) for var in ('self', 'cls', '__frame', '__file', '__func'))):
                continue
            print(f'<INTROSPECT> {__file}:{__func}:{k} - {v.__class__.__name__}')
        self.title = title
        self.link = link
