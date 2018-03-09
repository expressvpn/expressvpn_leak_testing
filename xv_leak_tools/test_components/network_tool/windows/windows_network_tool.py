import re

from xv_leak_tools.exception import XVEx
from xv_leak_tools.test_components.local_component import LocalComponent

class WindowsNetworkTool(LocalComponent):

    PROG_PING = re.compile(r".*Sent = ([\d]+), Received = ([\d]+).*")

    def __init__(self, device, config):
        super().__init__(device, config)
        # Import here to allow the file to be imported on any OS
        from xv_leak_tools.network.windows.windows_network import WindowsNetwork
        self._windows_network = WindowsNetwork

    def adapter_by_name(self, name):
        return self._windows_network.adapter_by_name(name)

    def adapter_by_net_connection_id(self, id_):
        return self._windows_network.adapter_by_net_connection_id(id_)

    def adapters_in_priority_order(self):
        return self._windows_network.adapters_in_priority_order()

    def primary_adapter(self):
        adapters = self.adapters_in_priority_order()
        pingable_adapters = [adapter for adapter in adapters if adapter.pingable()]
        if pingable_adapters:
            return pingable_adapters[0]
        raise XVEx("No pingable adapters. All adapters are {}".format(adapters))

    def report_info(self):
        ret = ''
        return ret

    def ping(self, ip="8.8.8.8", count=1, timeout=1, interface=None):
        '''Returns the number of packets lost when pinging. Note that interface needs to be an
        ip address on Windows.'''
        cmd = [
            "ping",
            "-n", "{}".format(count),
            "-w", "{}".format(timeout)
        ]
        if interface is not None:
            cmd += ["-S", interface]

        cmd.append(ip)
        ret, stdout, stderr = self._device.connector().execute(cmd)
        if not ret:
            return 0

        # Find number of packets lost
        for line in stdout.splitlines():
            match = WindowsNetworkTool.PROG_PING.match(line)
            if not match:
                continue
            return int(match.group(1)) - int(match.group(2))

        raise XVEx("Couldn't parse ping output\nstderr: {}\n stdout: {}".format(stderr, stdout))
