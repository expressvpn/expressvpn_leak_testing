from xv_leak_tools.exception import XVEx

class ComponentNotSupported(XVEx):
    pass

class Component: # pylint: disable=too-few-public-methods

    def __init__(self, device, config):
        self._device = device
        self._config = config

    def report_info(self):
        return "No info available for Component {}".format(self.__class__.__name__)

    def setup(self):
        pass

    def teardown(self):
        pass
