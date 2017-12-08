from xv_leak_tools.factory import Builder
from xv_leak_tools.test_components.component import ComponentNotSupported
from xv_leak_tools.test_components.network_tool.macos.macos_network_tool import MacOSNetworkTool
from xv_leak_tools.test_components.network_tool.linux.linux_network_tool import LinuxNetworkTool
from xv_leak_tools.test_components.network_tool.windows.windows_network_tool import WindowsNetworkTool

class NetworkToolBuilder(Builder):

    @staticmethod
    def name():
        return 'network_tool'

    def build(self, device, config):
        if device.os_name() == 'macos':
            return MacOSNetworkTool(device, config)
        elif device.os_name() == 'windows':
            return WindowsNetworkTool(device, config)
        elif device.os_name() == 'linux':
            return LinuxNetworkTool(device, config)
        else:
            raise ComponentNotSupported("network_tool is not currently supported on {}".format(
                device.os_name()))
