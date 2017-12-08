from xv_leak_tools.exception import XVEx
from xv_leak_tools.import_helpers import import_all_from_package, class_by_name, itersubclasses
from xv_leak_tools.test_framework.test_case import TestCase

# TODO: I'm even tempted to remove this and just make users specify the full path to the test
# in the config and have an attribute in the test file called TestClass (or similar)
class TestFactory:

    # pylint: disable=no-self-use
    # pylint: disable=too-few-public-methods

    def __init__(self, packages):
        self._packages = packages
        self._import_tests()

    @staticmethod
    def _check_test_classes_are_unique():
        '''Helper to check that no classes have duplicate names. We want tests to have unique names
        to avoid any confusion.'''
        all_test_classes = []
        for subclass in itersubclasses(TestCase):
            if not subclass.__name__.startswith("Test"):
                continue
            if subclass.__name__ in all_test_classes:
                raise XVEx(
                    "A test with name {} is defined twice. Please ensure test class names are "
                    "unique".format(subclass.__name__))
            all_test_classes.append(subclass.__name__)

    def _import_tests(self):
        for package in self._packages:
            import_all_from_package(package, restrict_platform=False)
        TestFactory._check_test_classes_are_unique()

    def create(self, name, devices, parameters):
        return class_by_name(name, TestCase)(devices, parameters)
