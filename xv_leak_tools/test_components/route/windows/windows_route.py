import re

import netaddr # pylint: disable=import-error

from xv_leak_tools.test_components.route.route import Route, RouteEntry
from xv_leak_tools.test_device.connector_helper import ConnectorHelper

class WindowsRoute(Route):

    PROG_ROW = re.compile(r"^\s*([^\s]+)\s+([^\s]+)\s+([^\s]+)\s+([^\s]+)\s+([^\s]+)$")

    def __init__(self, device, config):
        super().__init__(device, config)
        self._connector_helper = ConnectorHelper(self._device)

# Network Destination        Netmask          Gateway       Interface  Metric
#           0.0.0.0          0.0.0.0      172.16.49.2    172.16.49.174   2000
#           0.0.0.0          0.0.0.0    192.168.216.1  192.168.216.139  11000
#           0.0.0.0          0.0.0.0      172.16.49.2    172.16.49.173      2
#         127.0.0.0        255.0.0.0         On-link         127.0.0.1    331
#         127.0.0.1  255.255.255.255         On-link         127.0.0.1    331
#   127.255.255.255  255.255.255.255         On-link         127.0.0.1    331
#       169.254.0.0      255.255.0.0         On-link    169.254.25.248    262

    def get_v4_routes(self):
        routes = []
        lines = self._connector_helper.check_command(['netstat', '-rn'])[0].splitlines()
        for line in lines:
            if "Destination" in line:
                continue
            match = WindowsRoute.PROG_ROW.match(line)
            if not match:
                continue
            # Windows routes use IPs for the netmask rather than CIDR blocks.
            dest = "{}/{}".format(match.group(1), netaddr.IPAddress(match.group(2)).netmask_bits())
            entry = RouteEntry(
                dest=dest,
                gway=match.group(3),
                flags="",
                iface=match.group(4)
            )
            routes.append(entry)
        return routes
