from xv_leak_tools.exception import XVEx
from xv_leak_tools.log import L
from xv_leak_tools.test_components.vpn_application.android.android_vpn_application import AndroidVPNApplication
from xv_leak_tools.test_components.vpn_application.ios.ios_vpn_application import IOSVPNApplication
from xv_leak_tools.test_components.vpn_application.linux.linux_vpn_application import LinuxVPNApplication
from xv_leak_tools.test_components.vpn_application.macos.macos_vpn_application import MacOSVPNApplication
from xv_leak_tools.test_components.vpn_application.windows.windows_vpn_application import WindowsVPNApplication

class GenericVPNBuilder: # pylint: disable=too-few-public-methods

    def __init__(self, vpns):
        '''vpns is used to provide the paths to the apps. It should be a dict of dicts of the form:
            {
                'some_vpn': {
                    'macos': '/Applications/SomeVPN.app',
                    'windows': windows_safe_path(
                        "C:\\Program Files (x86)\\SomeVPN\\SomeVPN.exe"),
                    'linux': '/usr/bin/somevpn',
                },
            }

        The key 'some_vpn' is used in the test config to specify which VPN application to use.'''
        self._vpns = vpns

    @staticmethod
    def _build(os_name, vpn_info, device, config):
        if os_name == 'windows':
            return WindowsVPNApplication(
                vpn_info.get("app", None), vpn_info.get("tap", None), device, config)
        elif os_name == 'macos':
            return MacOSVPNApplication(vpn_info.get("app", None), device, config)
        elif os_name == 'linux':
            return LinuxVPNApplication(vpn_info.get("app", None), device, config)
        elif os_name == 'android':
            return AndroidVPNApplication(device, config)
        elif os_name == 'ios':
            return IOSVPNApplication(device, config)
        else:
            raise XVEx("Unknown OS '{}' when creating VPN application".format(os_name))

    def _vpn_info(self, vpn_name, os_name):
        if vpn_name not in self._vpns:
            L.warning("Don't know the VPN application {}. Known applications are {}".format(
                vpn_name, self._vpns.keys()))
            return {}
        return self._vpns[vpn_name][os_name]

    def build(self, device, config):
        os_name = device.os_name()
        vpn_info = self._vpn_info(config['name'], os_name)
        return GenericVPNBuilder._build(os_name, vpn_info, device, config)
