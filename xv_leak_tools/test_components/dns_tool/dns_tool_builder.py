from xv_leak_tools.exception import XVEx
from xv_leak_tools.factory import Builder
from xv_leak_tools.test_components.dns_tool.macos.macos_dns_tool import MacOSDNSTool
from xv_leak_tools.test_components.dns_tool.windows.windows_dns_tool import WindowsDNSTool
from xv_leak_tools.test_components.dns_tool.linux.linux_dns_tool import LinuxDNSTool
from xv_leak_tools.test_components.dns_tool.android.android_dns_tool import AndroidDNSTool

class DNSToolBuilder(Builder):

    @staticmethod
    def name():
        return 'dns_tool'

    def build(self, device, config):
        if device.os_name() == 'macos':
            return MacOSDNSTool(device, config)
        elif device.os_name() == 'windows':
            if device.is_cygwin():
                return WindowsDNSTool(device, config)
        elif device.os_name() == 'linux':
            return LinuxDNSTool(device, config)
        elif device.os_name() == 'android':
            return AndroidDNSTool(device, config)
        else:
            raise XVEx("Don't know how to build 'dns_tool' component for OS {}".format(
                device.os_name()))
