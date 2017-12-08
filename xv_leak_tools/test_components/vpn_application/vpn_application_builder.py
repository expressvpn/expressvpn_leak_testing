from xv_leak_tools.factory import Builder
from xv_leak_tools.path import windows_safe_path
from xv_leak_tools.test_components.vpn_application.generic_vpn_builder import GenericVPNBuilder

class VPNApplicationBuilder(Builder):

    VPNs = {
        'express_vpn': {
            'macos': {
                'app': '/Applications/ExpressVPN.app',
            },
            'windows': {
                'app': windows_safe_path(
                    "C:\\Program Files (x86)\\ExpressVPN\\xvpn-ui\\ExpressVpn.exe"),
                'tap': "ExpressVPN Tap Adapter",
            },
            'linux': {
                'app': '/usr/bin/expressvpn',
            },
        },
    }

    @staticmethod
    def name():
        return 'vpn_application'

    def build(self, device, config):
        return GenericVPNBuilder(VPNApplicationBuilder.VPNs).build(device, config)
