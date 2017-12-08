import re

from xv_leak_tools.exception import XVEx
from xv_leak_tools.log import L
from xv_leak_tools.test_components.local_component import LocalComponent

class MacOSNetworkTool(LocalComponent):

    # pylint: disable=no-self-use

    PROG_PING = re.compile(r"([\d]+) packets transmitted, ([\d]+) packets received.*")

    def __init__(self, device, config):
        super().__init__(device, config)
        # Import here to allow the file to be imported on any OS
        from xv_leak_tools.network.macos.locations_and_services import MacOSNetwork
        self._macos_network = MacOSNetwork

    def up_interfaces(self):
        return self._macos_network.up_interfaces()

    def network_services_in_priority_order(self):
        return self._macos_network.network_services_in_priority_order()

    def set_network_service_order(self, services):
        return self._macos_network.set_network_service_order(services)

    def wifi_service(self):
        return self._macos_network.wifi_service()

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
            match = MacOSNetworkTool.PROG_PING.match(line)
            if not match:
                continue
            return int(match.group(1)) - int(match.group(2))

        raise XVEx("Couldn't parse ping output\nstderr: {}\n stdout: {}".format(stderr, stdout))

    def _global_info(self):
        L.debug("Getting global info")
        ret = ''
        ret += 'Global Info\n'
        ret += '-----------\n\n'
        ret += "DNS Servers: {}\n\n".format(self._macos_network.dns_servers())
        return ret

    def _network_location_info(self):
        L.debug("Getting network location info")
        ret = ''
        ret += 'Network Locations\n'
        ret += '-----------------\n\n'
        location_data = []
        for location in self._macos_network.network_locations():
            data = ''
            data += "Name: {}\n".format(location.name())
            location_data.append(data)
        ret += '\n'.join(location_data)
        ret += '\n'
        return ret

    def _network_service_info(self):
        L.debug("Getting network service info")
        ret = ''
        ret += 'Network Services (Current Location)\n'
        ret += '-----------------------------------\n\n'
        service_data = []
        for service in self._macos_network.network_services_in_priority_order():
            data = ''
            data += "Name: {}\n".format(service.name())
            data += "ID: {}\n".format(service.id())
            data += "Type: {}\n".format(service.service_type_string())
            data += "Enabled: {}\n".format(service.enabled())
            data += "Active: {}\n".format(service.active())
            data += "IPv4 Addresses: {}\n".format(service.ipv4_addresses())
            data += "IPv6 Addresses: {}\n".format(service.ipv6_addresses())
            data += "DNS Servers: {}\n".format(service.dns_servers())
            data += "Mac Address: {}\n".format(service.mac_address())
            service_data.append(data)
        ret += '\n'.join(service_data)
        ret += '\n'
        return ret

    def report_info(self):
        ret = ''
        ret += self._global_info()
        ret += self._network_location_info()
        ret += self._network_service_info()
        return ret
