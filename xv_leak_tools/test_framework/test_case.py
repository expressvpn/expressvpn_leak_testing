import copy
from abc import ABCMeta

from xv_leak_tools.exception import XVEx
from xv_leak_tools.helpers import is_root_user
from xv_leak_tools.log import L
from xv_leak_tools.test_framework.assertions import Assertions, LeakTestFail

class SupportedParameter:

    # pylint: disable=too-few-public-methods

    def __init__(self, default=None, required=False, docs=None):
        self.default = default
        self.required = required
        self.docs = docs

# Many derived test cases have abstract methods. To keep things simple we make the TestCase
# base class's meta class ABC so we don't have to repeat this in other places.
class TestCase(Assertions, metaclass=ABCMeta):

    def __init__(self, devices, parameters):
        self.devices = devices
        self.parameters = self._clean_parameters(parameters)

        if self.__class__.requires_root() and not is_root_user():
            # TODO: Consider throwing an exception like TestCannotRunOnThisMachine
            raise LeakTestFail("Test requires root permissions")

    # Default is to assume we need root for now.
    @staticmethod
    def requires_root():
        return True

    @staticmethod
    def supported_parameters():
        return {}

    def _clean_parameters(self, parameters):
        supported_parameters = self.supported_parameters()
        for name, _ in list(parameters.items()):
            if name not in supported_parameters:
                L.warning("Parameter {} not supported for test {}. It will be ignored".format(
                    name, self.__class__.__name__))
                continue

        for name, supported_parameter in list(supported_parameters.items()):
            if name not in parameters:
                if supported_parameter.required:
                    raise XVEx("Parameter {} is mandatory for test {}".format(
                        name, self.__class__.__name__))
                else:
                    L.debug("Defaulting test parameter '{}' to {}".format(
                        name, copy.deepcopy(supported_parameter.default)))
                    parameters[name] = supported_parameter.default
        return parameters

    def setup(self):
        pass

    def teardown(self):
        pass

    def test(self):
        pass

    def report_info(self):
        L.report("Test: {}\n".format(self.__class__.__name__))
        for device_name, device in list(self.devices.items()):
            L.report("Device: {}".format(device_name))
            L.report(device.report_info())
