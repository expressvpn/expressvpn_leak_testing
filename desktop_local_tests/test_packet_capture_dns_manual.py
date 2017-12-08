from desktop_local_tests.local_packet_capture_test_case import LocalPacketCaptureTestCase
from xv_leak_tools.log import L
from xv_leak_tools.manual_input import message_and_await_enter

class TestPacketCaptureDNSManual(LocalPacketCaptureTestCase):

    '''Summary:

    Test whether traffic leaks outside of the VPN tunnel during regular operation of the VPN.

    Details:

    This test connects to the VPN then starts packet capture to monitor all outgoing traffic from
    the device. It then checks to see if any traffic leaked outside of the VPN. The test allows
    the user an arbitrary window in which to generate traffic and thus is inherently a manual test.

    The test is almost identical to TestPacketCaptureVanilla but allows for indefinite manual
    control of the machine rather than a timed wait.

    Discussion:

    It is useful for investigating scenarios which might leak. If a leak is found a more specific
    test should be made.

    The test is a basic template for all packet capture based tests. The manual step can in
    principal be replaced by any form of traffic generation.

    Weaknesses:

    Packet capture tests can be noisy. Traffic can be detected as a leak but in actual fact may not
    be. For example, traffic might go to a server owned by the VPN provider to re-establish
    connections. In general this test is best used for manual exploring leaks rather than for
    automation.

    Scenarios:

    No restrictions.
    '''

    def filter_packets(self, packets):
        # Don't use the parent filter. We want to be stricter here. Local traffic is okay. For
        # example, suppose I'm testing a VM guest and the host uses local DNS. Then the traffic
        # will look like local->local:53. We don't want to filter that out. That would be a leak.
        unmatched = self.traffic_filter.filter_traffic(packets, multicast=True)[1]
        just_port_53_packets = self.traffic_filter.filter_traffic(unmatched, dst_port=53)[0]
        return just_port_53_packets

    def test_with_packet_capture(self):
        L.describe('Generate DNS traffic')
        message_and_await_enter(
            "Generate traffic however you want. Packet capture will continue in the background. "
            "When you're done press enter to check if anything leaked.")
