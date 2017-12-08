from xv_leak_tools.factory import Builder
from xv_leak_tools.test_components.webdriver.webdriver import XVDriverLinux, XVDriverMacOS, XVDriverWindows
from xv_leak_tools.test_components.component import ComponentNotSupported

class WebdriverBuilder(Builder):
    # TODO: Test this on MacOS, Windows

    @staticmethod
    def name():
        return 'webdriver'

    def build(self, device, config):
        if device.os_name() == 'linux':
            return XVDriverLinux(device, config)
        elif device.os_name() == 'macos':
            return XVDriverMacOS(device, config)
        elif device.os_name() == 'windows':
            return XVDriverWindows(device, config)
        raise ComponentNotSupported("Can't build a webdriver on {}".format(device.os_name()))
