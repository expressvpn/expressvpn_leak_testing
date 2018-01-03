from xv_leak_tools.exception import XVEx
from xv_leak_tools.log import L
from xv_leak_tools.test_components.vpn_application.desktop_vpn_application import DesktopVPNApplication

class WindowsVPNApplication(DesktopVPNApplication):

    def __init__(self, app_path, tap_adapter_name, device, config):
        super().__init__(app_path, device, config)
        self._tap_adapter_name = self._get_full_tap_adapter_name(tap_adapter_name)

    def _get_full_tap_adapter_name(self, tap_adapter_name):
        if tap_adapter_name is None:
            return None
        # The logic here is necessary because Windows can give the TAP adapters suffixes like #2.
        # So the name might not match exactly what we expect. I think this happens when there's a
        # name collision. If we have two adapters with the same name then let's error as it's
        # probably going to cause a problem.
        L.debug("Looking for TAP adapter with name '{}'".format(tap_adapter_name))
        adapters = self._device['network_tool'].adapters_in_priority_order()
        candidates = []
        for adapter in adapters:
            adapter_name = adapter.name()
            if tap_adapter_name == adapter_name:
                # If we find an exact match then just return it
                return adapter_name
            if adapter_name.startswith(tap_adapter_name):
                candidates.append(adapter_name)
        if len(candidates) == 1:
            L.debug("Found TAP adapter with name '{}'".format(candidates[0]))
            return candidates[0]
        if len(candidates) == 0:
            raise XVEx("Found no candidate adapters matching TAP adapter '{}' for '{}':\n{}".format(
                tap_adapter_name, self._config['name'], candidates))
        raise XVEx("Found several candidate adapters matching TAP adapter '{}' for '{}':\n{}".format(
            tap_adapter_name, self._config['name'], candidates))

    def dns_server_ips(self):
        if not self._tap_adapter_name:
            L.debug(
                "Don't know TAP adapter name for VPN application {}. Falling back to default "
                "method to get DNS server IPs".format(self._config["name"]))
            return super().dns_server_ips()

        adapters = self._device['network_tool'].adapter_by_name(self._tap_adapter_name)
        if adapters:
            return adapters[0].dns_servers()

        L.warning(
            "Couldn't find TAP adapter '{}' for VPN application '{}'. Falling back to default "
            "method to get DNS server IPs".format(self._tap_adapter_name, self._config["name"]))
        return super().dns_server_ips()

    def tunnel_interface(self):
        if self._tap_adapter_name:
            return self._tap_adapter_name
        return super().tunnel_interface()
