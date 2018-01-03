import ipaddress

from xv_leak_tools.log import L
from xv_leak_tools.exception import XVEx
from xv_leak_tools.network.common import is_mac_address
from xv_leak_tools.test_components.component import Component
from xv_leak_tools.test_components.packet_capturer.packets import Packets
from xv_leak_tools.test_components.packet_capturer.posix.posix_go_packet_capturer import PosixGoPacketCapturer
from xv_leak_tools.test_components.packet_capturer.windows.windows_go_packet_capturer import WindowsGoPacketCapturer

# This class has too much if platorm else platform. We should abstract and derive
class PacketCapturer(Component):

    def __init__(self, device, config):
        super().__init__(device, config)
        self._config = config
        self._capturers = []

    def _create_go_packet_capture(self, device, interface):
        if self._device.os_name() == "windows":
            return WindowsGoPacketCapturer(device, interface)
        return PosixGoPacketCapturer(device, interface)

    def _get_primary_interface(self):
        # TODO: Tidy this up. I don't like having to if-else this. I think we need the network_tool
        # component to be OS neutral and then, for the situations where we need it, have a
        # macos_network_tool, windows_network_tool etc.
        # Also note that we use this logic a lot of getting primary service/adapter. This can be
        # DRYed
        if self._device.os_name() == "windows":
            adapters = self._device['network_tool'].adapters_in_priority_order()
            primary_adapter = [adapter for adapter in adapters if adapter.enabled()][0]
            return primary_adapter.windump_index()

        services = self._device['network_tool'].network_services_in_priority_order()
        return [service.interface() for service in services if service.active()][0]

    def _get_non_tunnel_interfaces(self):
        if not self._device['vpn_application']:
            raise XVEx(
                "Capturing on 'non-tunnel' interfaces only makes sense if the VPN "
                "application is running on the same device as traffic capture")

        if self._device.os_name() == "windows":
            non_tunnel_adapters = []
            adapters = self._device['network_tool'].adapters_in_priority_order()
            adapters = [adapter for adapter in adapters if adapter.enabled()]
            tun = self._device['vpn_application'].tunnel_interface()
            for adapter in adapters:
                if adapter.name() == tun:
                    continue
                non_tunnel_adapters.append(adapter)
            names = [adapter.net_connection_id() for adapter in non_tunnel_adapters]
            L.info("Windows non-tunnel adapters are: {}".format(names))
            return [adapter.windump_index() for adapter in non_tunnel_adapters]
        elif self._device.os_name() == "macos":
            services = self._device['network_tool'].network_services_in_priority_order()
            interfaces = [service.interface() for service in services if service.active()]
            return interfaces
        else:
            # TODO: get this working on Linux -- probably just copy macos.
            interfaces = self._get_all_interfaces()
            tun = self._device['vpn_application'].tunnel_interface()
            if tun not in interfaces:
                raise XVEx(
                    "Something went wrong. Didn't find the VPN tunnel interface '{}' in the list "
                    "of active interfaces: {}".format(tun, interfaces))
            interfaces.remove(tun)
            return interfaces

    def _get_all_interfaces(self):
        if self._device.os_name() == "windows":
            adapters = self._device['network_tool'].adapters_in_priority_order()
            return [adapter.windump_index() for adapter in adapters if adapter.enabled()]

        services = self._device['network_tool'].network_services_in_priority_order()
        return [service.interface() for service in services if service.active()]

    def default_interfaces(self):
        L.info(
            "No interfaces specified for packet capture. Checking config to determine which to use")

        if 'capture_interface' not in self._config:
            raise XVEx("Specify the 'capture_interface' in the 'packet_capturer' component config")

        if self._config['capture_interface'] == 'span':
            interface = self._device.config()['span_interface']
            L.info("Using span interface for capture: {}".format(interface))
            return [interface]
        elif self._config['capture_interface'] == 'primary':
            interface = self._get_primary_interface()
            L.info("Using primary interface for capture: {}".format(interface))
            return [interface]
        elif self._config['capture_interface'] == 'non-tunnel':
            interfaces = self._get_non_tunnel_interfaces()
            L.info("Using non-tunnel interfaces for capture: {}".format(interfaces))
            return interfaces
        elif self._config['capture_interface'] == 'all':
            interfaces = self._get_all_interfaces()
            L.info("Using all interfaces for capture: {}".format(interfaces))
            return interfaces
        else:
            raise XVEx("Don't know how to handle capture_interface '{}'".format(
                self._config['capture_interface']))

    def start(self, interfaces=None):
        if self._capturers:
            raise XVEx("Packet capturer already running")

        interfaces = interfaces or self.default_interfaces()
        for interface in interfaces:
            L.info('Starting packet capture on interface {}'.format(interface))
            self._capturers.append(self._create_go_packet_capture(self._device, interface))
            self._capturers[-1].start()

    def stop(self):
        L.info('Stopping packet capture and getting packets')
        packets = []
        for capturer in self._capturers:
            packets += capturer.stop()

        # TODO: Fix these issues in the capturer itself?
        packets = [packet for packet in packets if packet['DestIP']]
        packets = [packet for packet in packets if not is_mac_address(packet['DestIP'])]
        for packet in packets:
            packet['SourceIP'] = ipaddress.ip_address(packet['SourceIP'])
            packet['DestIP'] = ipaddress.ip_address(packet['DestIP'])

        if not packets:
            L.warning('No packets were captured. This is probably not what you want.')
        else:
            L.info('{} packets captured'.format(len(packets)))
            L.verbose("List of all packets:\n{}".format(Packets(packets)))
        return packets
