from desktop_local_tests.local_packet_capture_test_case import LocalPacketCaptureTestCase
from xv_leak_tools.log import L
from xv_leak_tools.test_framework.test_case import SupportedParameter

class TestPacketCaptureDNSUntunneledVanilla(LocalPacketCaptureTestCase):

    URL = "https://www.expressvpn.com/dns-leak-test"

    def __init__(self, devices, config):
        super().__init__(devices, config)
        self.webdriver = self.localhost['webdriver'].driver(self.parameters['browser'])

    @staticmethod
    def supported_parameters():
        return {
            'browser': SupportedParameter(
                required=True,
                docs='Browser to use to generate traffic'),
            'allow_vpn_sever_ip': SupportedParameter(
                default=False,
                required=False,
                docs="Set if you don't want to consider traffic which goes to the VPN DNS Server "
                     "IP a leak *even* if it went outside of the tunnel"),
        }

    def filter_packets(self, packets):
        # Don't use the parent filter. We want to be stricter here. Local traffic is okay. For
        # example, suppose I'm testing a VM guest and the host uses local DNS. Then the traffic
        # will look like local->local:53. We don't want to filter that out. That would be a leak.
        unmatched = self.traffic_filter.filter_traffic(packets, multicast=True)[1]
        just_port_53_packets = self.traffic_filter.filter_traffic(unmatched, dst_port=53)[0]

        # This test can be run in a mode where we consider traffic to the VPN server to not be a
        # leak, even though it's not going through the tunnel. It helps drill down into how severe
        # leaks are for a VPN.
        if self.parameters.get("allow_vpn_sever_ip", False):
            just_port_53_packets = self.traffic_filter.filter_traffic(
                just_port_53_packets, dst_ip=self.localhost['vpn_application'].dns_server_ips())[1]

        return just_port_53_packets

    def test_with_packet_capture(self):
        L.describe("Generate traffic by visiting this website: {}".format(
            TestPacketCaptureDNSUntunneledVanilla.URL))
        self.webdriver.get(TestPacketCaptureDNSUntunneledVanilla.URL)
        self.webdriver.close()
