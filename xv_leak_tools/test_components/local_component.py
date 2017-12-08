from xv_leak_tools.test_components.component import Component, ComponentNotSupported
from xv_leak_tools.test_device.local_shell_connector import LocalShellConnector

class LocalComponent(Component):

    def __init__(self, device, config):
        super().__init__(device, config)
        self._check_connector_is_local()

    def _check_connector_is_local(self):
        if isinstance(self._device.connector(), LocalShellConnector):
            return

        raise ComponentNotSupported(
            "Component {} can only be used directly on device. It will not work remotely".format(
                self.__class__.__name__))
