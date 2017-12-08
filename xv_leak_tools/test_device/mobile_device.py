from abc import abstractmethod
from xv_leak_tools.test_device.device import Device

class MobileDevice(Device):

    @abstractmethod
    def wakeup(self):
        pass

    @abstractmethod
    def sleep(self):
        pass
