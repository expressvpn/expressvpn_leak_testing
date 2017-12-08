from xv_leak_tools.factory import Builder

from xv_leak_tools.log import L
from xv_leak_tools.test_components.component import ComponentNotSupported
from xv_leak_tools.test_components.firewall.macos.macos_firewall import MacOSFirewall
from xv_leak_tools.test_components.firewall.windows.windows_firewall import WindowsFirewall
from xv_leak_tools.test_device.desktop_device import DesktopDevice

class FirewallBuilder(Builder):

    @staticmethod
    def name():
        return 'firewall'

    def build(self, device, config):
        if not isinstance(device, DesktopDevice):
            raise ComponentNotSupported(
                "Can't create firewall tool for : {}".format(device.os_name()))

        if device.os_name() == 'macos':
            return MacOSFirewall(device, config)
        elif device.os_name() == 'windows':
            return WindowsFirewall(device, config)
        elif device.os_name() == 'linux':
            L.warning("Firewall not implemented for linux yet")
            raise ComponentNotSupported("Firewall not implemented for linux yet")
