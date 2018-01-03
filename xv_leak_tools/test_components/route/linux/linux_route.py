import netaddr
import re

from xv_leak_tools.exception import XVEx
from xv_leak_tools.test_components.route.route import Route, RouteEntry
from xv_leak_tools.test_device.connector_helper import ConnectorHelper

class LinuxRoute(Route):

    PROG_ROW = re.compile(
        r"^([^\s]+)\s+([^\s]+)\s+([^\s]+)\s+([^\s]+)\s+([^\s]+)\s+([^\s]+)\s+([^\s]+)\s+([^\s]+)\s*$")

    def __init__(self, device, config):
        super().__init__(device, config)
        self._connector_helper = ConnectorHelper(self._device)

# Kernel IP routing table
# Destination     Gateway         Genmask         Flags   MSS Window  irtt Iface
# 0.0.0.0         172.16.49.2     0.0.0.0         UG        0 0          0 ens33
# 169.254.0.0     0.0.0.0         255.255.0.0     U         0 0          0 ens33
# 172.16.49.0     0.0.0.0         255.255.255.0   U         0 0          0 ens33

    def get_v4_routes(self):
        routes = []
        lines = self._connector_helper.check_command(['netstat', '-rn'])[0].splitlines()
        for line in lines:
            if "Destination" in line:
                continue
            match = LinuxRoute.PROG_ROW.match(line)
            print(line)
            if not match:
                continue
            # Windows routes use IPs for the netmask rather than CIDR blocks.
            dest = "{}/{}".format(match.group(1), netaddr.IPAddress(match.group(3)).netmask_bits())
            entry = RouteEntry(
                dest=dest,
                gway=match.group(2),
                flags=match.group(4),
                iface=match.group(8),
            )
            routes.append(entry)
        return routes
