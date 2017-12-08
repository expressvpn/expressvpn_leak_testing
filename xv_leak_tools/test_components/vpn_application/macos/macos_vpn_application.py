from xv_leak_tools.log import L
from xv_leak_tools.test_components.vpn_application.desktop_vpn_application import DesktopVPNApplication

class MacOSVPNApplication(DesktopVPNApplication):

    def __init__(self, app_path, device, config):
        super().__init__(app_path, device, config)
        self._dns_servers_before_connect = device['dns_tool'].known_servers()

    def dns_server_ips(self):
        info = self._vpn_info()
        if info is not None and info.dns_server_ips:
            return info.dns_server_ips

        if not self._config.get('strict', False):
            dns_servers_after_connect = set(self._device['dns_tool'].known_servers())
            L.debug(
                "Inferring VPN DNS servers. DNS before connect: {}, DNS after connect: {}".format(
                    self._dns_servers_before_connect, dns_servers_after_connect))

            for server in self._dns_servers_before_connect:
                dns_servers_after_connect.discard(server)

            if dns_servers_after_connect:
                L.warning("Inferring VPN DNS server IPs from System Configuration. "
                          "This is likely correct, but can be prevented by specifying "
                          "the 'strict' keyword in the VPN configuration.")
                return list(dns_servers_after_connect)
            L.warning("Couldn't find DNS servers by inspecting system.")

        return super().dns_server_ips()
