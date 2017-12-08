from xv_leak_tools.log import L
from xv_leak_tools.test_device.device import Device

class RouterDevice(Device):

    def os_name(self):
        # TODO: Make this dynamic
        return 'linux'

    def os_version(self):
        L.warning("TODO: Linux version")
        return 'TODO: Linux version'
