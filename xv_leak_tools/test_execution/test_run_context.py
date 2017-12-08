import sys

from xv_leak_tools.factory import Factory
from xv_leak_tools.test_framework.test_factory import TestFactory

class TestRunContext:

    # pylint: disable=too-few-public-methods

    def __init__(self, context_dict):
        self._context_dict = context_dict
        self._set_sys_path()

    def __getitem__(self, key):
        if key == 'component_factory':
            return Factory(self._context_dict['component_packages'])
        elif key == 'test_factory':
            return TestFactory(self._context_dict['test_packages'])
        return self._context_dict[key]

    def _set_sys_path(self):
        for path in self._context_dict['package_paths']:
            sys.path.append(path)
