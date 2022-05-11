
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional
from great_expectations.types import SerializableDictDot

class TestData(dict):
    __test__ = False
    pass

class Backend(Enum):
    'Backends with some level of testing and support'
    BIGQUERY = 'CONCEPT_ONLY'
    MSSQL = 'EXPERIMENTAL'
    SQLITE = 'BETA'
    PYSPARK = 'PRODUCTION'

@dataclass
class TestBackend():
    backend: str
    dialects: Optional[List[str]]
    __test__ = False

    def __post_init__(self) -> None:
        import inspect
        __frame = inspect.currentframe()
        __file = __frame.f_code.co_filename
        __func = __frame.f_code.co_name
        for (k, v) in __frame.f_locals.items():
            if any(((var in k) for var in ('self', 'cls', '__frame', '__file', '__func'))):
                continue
            print(f'<INTROSPECT> {__file}:{__func}:{k} - {v.__class__.__name__}')
        allowed_backend_names = ('pandas', 'spark', 'sqlalchemy')
        allowed_sql_dialects = ('sqlite', 'postgresql', 'mysql', 'mssql', 'bigquery')
        assert (self.backend in allowed_backend_names), f'backend must be one of {allowed_backend_names}, not {self.backend}'
        if (self.backend != 'sqlalchemy'):
            assert (self.dialects is None), f'You may not specify dialects for backend {self.backend}'
        else:
            assert ((type(self.dialects) == list) and (len(self.dialects) > 0)), 'dialects must be a list for backend sqlalchemy'
            bad_dialects = [dialect for dialect in self.dialects if (dialect not in allowed_sql_dialects)]
            assert (bad_dialects == []), f'dialects can only include {allowed_sql_dialects}, not {bad_dialects}'

@dataclass
class ExpectationTestCase(SerializableDictDot):
    'A single test case, with input arguments and output'
    title: str
    input: Dict[(str, Any)]
    output: Dict[(str, Any)]
    exact_match_out: bool
    suppress_test_for: List[str] = field(default_factory=list)
    include_in_gallery: bool = False
    only_for: Optional[List[str]] = None

class ExpectationLegacyTestCaseAdapter(ExpectationTestCase):
    'This class provides an adapter between the test cases developed prior to Great Expectations\' 0.14 release and the newer ExpectationTestCase dataclass\n\n    Notes:\n    * Legacy test cases used "in" (a python reserved word). This has been changed to "input".\n    * To maintain parallelism, we\'ve also made the corresponding change from "out" to "output".\n    * To avoid any ambiguity, ExpectationLegacyTestCaseAdapter only accepts keyword arguments. Positional arguments are not allowed.\n    '

    def __init__(self, *, title, exact_match_out, out, suppress_test_for=[], **kwargs) -> None:
        import inspect
        __frame = inspect.currentframe()
        __file = __frame.f_code.co_filename
        __func = __frame.f_code.co_name
        for (k, v) in __frame.f_locals.items():
            if any(((var in k) for var in ('self', 'cls', '__frame', '__file', '__func'))):
                continue
            print(f'<INTROSPECT> {__file}:{__func}:{k} - {v.__class__.__name__}')
        super().__init__(title=title, input=kwargs['in'], output=out, exact_match_out=exact_match_out, suppress_test_for=suppress_test_for, only_for=kwargs.get('only_for'), include_in_gallery=kwargs.get('include_in_gallery', False))

@dataclass
class ExpectationTestDataCases(SerializableDictDot):
    'Pairs a test dataset and a list of test cases to execute against that data.'
    data: TestData
    tests: List[ExpectationTestCase]
    schemas: Dict[(Backend, Dict[(str, str)])] = field(default_factory=dict)
    test_backends: Optional[List[TestBackend]] = None
    data_alt: Optional[TestData] = None
