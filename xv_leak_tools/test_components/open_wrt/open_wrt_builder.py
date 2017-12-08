from xv_leak_tools.factory import Builder
from xv_leak_tools.test_components.component import ComponentNotSupported
from xv_leak_tools.test_components.open_wrt.open_wrt import OpenWRT

class OpenWRTBuilder(Builder):

    @staticmethod
    def name():
        return 'open_wrt'

    def build(self, device, config):
        if device.os_name() != 'linux':
            raise ComponentNotSupported(
                "Can't create open_wrt tools for : {}".format(device.os_name()))

        return OpenWRT(device, config)
