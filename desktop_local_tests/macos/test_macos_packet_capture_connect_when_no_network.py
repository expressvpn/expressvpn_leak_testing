import json

from desktop_local_tests.local_packet_capture_test_case import LocalPacketCaptureTestCase
from xv_leak_tools.log import L

class TestMacOSPacketCaptureConnectWhenNoNetwork(LocalPacketCaptureTestCase):

    '''Summary:

    Test the behaviour of VPN applications when the user tries to connect with no network
    connectivity.

    Details:

    This test initiates a VPN connection when there's no network connectivity. It then subsequently
    enables a network connection and then tests to see if any traffic leaks in the period between
    regaining network connectivity and the app establishing a VPN connection.

    Discussion:

    For some applications this test will not make a lot of sense. For ExpressVPN we always expect
    that once the user chooses to start a connection they will be in a protected state until they
    consciously choose to disconnect.

    Weaknesses:

    Once the network connection is established the behaviour of apps may differ. The test
    currently just `connect`s the VPN application, however this in general might not be the
    correct thing to do. Indeed, with ExpressVPN there is a "Try Again" button, which is not
    directly correlated with the notion of "connect" (since the user at this stage has already
    chosen to connect). For other applications the behaviour might be any of the following:

        * App offers no protection in this scenario
        * App doesn't offer a way to retry connection when it fails
        * App requires some other interaction for the user to reestablish the connection

    Scenarios:

    No restrictions.
    '''

    def __init__(self, devices, config):
        super().__init__(devices, config)
        self.original_active_services = None

    def test(self):
        services = self.localhost['network_tool'].network_services_in_priority_order()
        interfaces = [service.interface() for service in services if service.active()]
        self.original_active_services = [service for service in services if service.active()]
        primary_service = self.original_active_services[0]

        L.describe('Disable all active services')
        for service in self.original_active_services:
            service.disable()

        L.describe('Open and connect the VPN application')
        self.localhost['vpn_application'].open_and_connect()

        L.describe('Capture traffic')
        self.localhost['packet_capturer'].start(interfaces)

        L.describe('Wait for the VPN application to notice the interruption')
        self.localhost['vpn_application'].wait_for_connection_interrupt_detection()

        L.describe('Enable primary network service')
        primary_service.enable()
        L.info("Enabled {}".format(primary_service))

        L.describe('Reconnect the VPN')
        # TODO: Let's consider if there's a more general way to do this. Potentially we can make
        # a manual step here which asks the user to ensure the app reconnects. For automation of
        # XV we can consider an override which does the appropriate thing.
        self.localhost['vpn_application'].connect()

        L.describe('Determine the VPN server IP')
        vpn_server_ip = self.localhost['vpn_application'].vpn_server_ip()
        L.info("VPN server IP is {}".format(vpn_server_ip))

        L.describe('Stop capturing traffic')
        self.localhost['packet_capturer'].stop()

        L.describe('Analyse packets to ensure we saw no traffic leaking')
        packets = self.localhost['packet_capturer'].get_capture(interfaces)

        # TODO: Consider only filtering local traffic if LAN block is not on.
        unmatched = self.traffic_filter.filter_traffic(packets, local=True)[1]
        unmatched = self.traffic_filter.filter_traffic(unmatched, link_local=True)[1]
        unmatched = self.traffic_filter.filter_traffic(unmatched, multicast=True)[1]
        unmatched = self.traffic_filter.filter_traffic(unmatched, dst_ip=True)[1]

        self.assertEmpty(unmatched, json.dumps(unmatched, indent=2))

    def teardown(self):
        for service in self.original_active_services:
            if not service.enabled():
                service.enable()
        super().teardown()
