from desktop_local_tests.local_packet_capture_test_case_with_disrupter import LocalPacketCaptureTestCaseWithDisrupter
from xv_leak_tools.log import L

class LocalPacketCaptureTestCaseWithDisrupterAndGenerator(LocalPacketCaptureTestCaseWithDisrupter):

    def __init__(self, disrupter_class, devices, parameters):
        super().__init__(disrupter_class, devices, parameters)
        self.webdriver = None

    def filter_packets(self, packets):
        # Don't use the parent filter. We want to be stricter here. Local traffic is okay. For
        # example, suppose I'm testing a VM guest and the host uses local DNS. Then the traffic
        # will look like local->local:53. We don't want to filter that out. That would be a leak.
        gateway = self.localhost['vpn_application'].tunnel_gateway()
        unmatched = self.traffic_filter.filter_traffic(packets, multicast=True)[1]
        unmatched = self.traffic_filter.filter_traffic(packets, dst_ip=gateway)[1]
        just_port_53_packets = self.traffic_filter.filter_traffic(unmatched, dst_port=53)[0]
        return just_port_53_packets

    def test_with_packet_capture(self):
        L.describe("Create disruption...")
        self.disrupter.create_disruption()
        L.describe("Generate traffic")
        self.webdriver = self.localhost['webdriver'].driver(self.parameters['browser'])
        self.webdriver.get("https://www.expressvpn.com/dns-leak-test")

    def teardown(self):
        if self.webdriver:
            self.webdriver.quit()
        super().teardown()
