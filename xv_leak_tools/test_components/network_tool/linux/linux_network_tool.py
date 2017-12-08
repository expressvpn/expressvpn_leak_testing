import re

from xv_leak_tools.exception import XVEx
from xv_leak_tools.test_components.local_component import LocalComponent

class LinuxNetworkTool(LocalComponent):

    PROG_PING = re.compile(r"([\d]+) packets transmitted, ([\d]+) packets received.*")

    def __init__(self, device, config):
        super().__init__(device, config)
        from xv_leak_tools.network.linux.network_services import LinuxNetwork
        self._linux_network = LinuxNetwork

    def network_services_in_priority_order(self):
        return self._linux_network.network_services_in_priority_order()

    # TODO: Untested on linux. Will likely fail
    def ping(self, ip="8.8.8.8", count=1, timeout=1, interface=None):
        '''Returns the number of packets lost when pinging'''
        cmd = [
            "ping",
            "-c{}".format(count),
            "-W{}".format(timeout)
        ]
        if interface is not None:
            cmd += ["-b", interface]

        cmd.append(ip)
        ret, stdout, stderr = self._device.connector().execute(cmd)
        if not ret:
            return 0

        # Find number of packets lost
        for line in stdout.splitlines():
            match = LinuxNetworkTool.PROG_PING.match(line)
            if not match:
                continue
            return int(match.group(1)) - int(match.group(2))

        raise XVEx("Couldn't parse ping output\nstderr: {}\n stdout: {}".format(stderr, stdout))
