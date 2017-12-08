# pylint: skip-file
from xv_leak_tools.test_components.vpn_application.desktop_vpn_application import DesktopVPNApplication

# TODO: Placeholder for now. Doesn't do anything special
class LinuxVPNApplication(DesktopVPNApplication):

    def __init__(self, app_path, device, config):
        super().__init__(app_path, device, config)
