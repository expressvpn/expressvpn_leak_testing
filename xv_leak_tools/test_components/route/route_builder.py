from xv_leak_tools.factory import Builder
from xv_leak_tools.test_components.route.macos.macos_route import MacOSRoute
from xv_leak_tools.test_components.route.windows.windows_route import WindowsRoute
from xv_leak_tools.test_components.route.linux.linux_route import LinuxRoute
from xv_leak_tools.test_components.component import ComponentNotSupported

class RouteBuilder(Builder):

    @staticmethod
    def name():
        return 'route'

    def build(self, device, config):
        if device.os_name() == 'linux':
            return LinuxRoute(device, config)
        elif device.os_name() == 'macos':
            return MacOSRoute(device, config)
        elif device.os_name() == 'windows':
            return WindowsRoute(device, config)
        raise ComponentNotSupported("Can't build a route component on {}".format(device.os_name()))
