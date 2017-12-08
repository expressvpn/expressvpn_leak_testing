import inspect

from xv_leak_tools.import_helpers import import_all_from_package, itersubclasses
from xv_leak_tools.test_framework.test_case import TestCase
from xv_leak_tools.test_documentation.docstring_helpers import trim_docstring

class TestDocstringRead:

    # pylint: disable=too-few-public-methods

    def __init__(self, test_packages):
        self._test_packages = test_packages
        self._test_docs = None

    def _read_docs(self):
        self._test_docs = {}
        for package in self._test_packages:
            import_all_from_package(package, restrict_platform=False)

        for subclass in itersubclasses(TestCase):
            if not subclass.__name__.startswith("Test"):
                continue
            self._test_docs[subclass.__name__] = {
                'file': inspect.getfile(subclass.__class__),
                'doc': None if subclass.__doc__ is None else trim_docstring(subclass.__doc__),
            }

    def docs(self):
        if self._test_docs is None:
            self._read_docs()
        return self._test_docs
