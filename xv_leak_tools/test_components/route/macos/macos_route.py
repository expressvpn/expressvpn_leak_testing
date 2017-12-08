import re

from xv_leak_tools.test_components.route.route import Route, RouteEntry
from xv_leak_tools.test_device.connector_helper import ConnectorHelper

class MacOSRoute(Route):

    PROG_ROW = re.compile(
        r"^([^\s]+)\s+([^\s]+)\s+([^\s]+)\s+([^\s]+)\s+([^\s]+)\s+([^\s]+)\s*([^\s]*)$")

    def __init__(self, device, config):
        super().__init__(device, config)
        self._connector_helper = ConnectorHelper(self._device)

# Internet:
# Destination        Gateway            Flags        Refs      Use   Netif Expire
# default            192.168.56.1       UGSc          100       90     en0
# default            192.168.104.1      UGScI           1        0     en4
# default            192.168.216.1      UGScI           0        0   vlan0

    def get_v4_routes(self):
        routes = []
        lines = self._connector_helper.check_command(['netstat', '-rn'])[0].splitlines()
        for line in lines:
            if "Destination" in line:
                continue
            match = MacOSRoute.PROG_ROW.match(line)
            if not match:
                continue
            entry = RouteEntry(
                dest=match.group(1),
                gway=match.group(2),
                flags=match.group(3),
                refs=match.group(4),
                use=match.group(5),
                iface=match.group(6),
                expire=match.group(7)
            )
            routes.append(entry)
        return routes
