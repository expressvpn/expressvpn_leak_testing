from abc import abstractmethod
from xv_leak_tools.test_device.device import Device

class DesktopDevice(Device):

    @abstractmethod
    def os_name(self):
        pass

    @abstractmethod
    def os_version(self):
        pass

    def _check_config(self, extra_keys=None):
        super()._check_config(['tools_root'])

    def tools_root(self):
        return self._config['tools_root']
