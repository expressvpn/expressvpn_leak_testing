import math
import time

from desktop_local_tests.local_test_case import LocalTestCase
from xv_leak_tools.helpers import TimeUp
from xv_leak_tools.log import L
from xv_leak_tools.test_components.packet_capturer.packets import Packets
from xv_leak_tools.traffic_filter import TrafficFilter

class LocalPacketCaptureTestCase(LocalTestCase):

    DEFAULT_CHECK_PERIOD = 0

    def __init__(self, devices, config):
        super().__init__(devices, config)
        self.traffic_filter = TrafficFilter
        self.initial_vpn_server_ip = None
        self.final_vpn_server_ip = None
        if 'capture_device' in self.devices:
            self.capture_device = self.devices['capture_device']
        else:
            self.capture_device = self.localhost

    def test_with_packet_capture(self):
        pass

    def start_traffic_generation(self): # pylint: disable=no-self-use
        L.info("No traffic generation being done for this test")

    def stop_traffic_generation(self):
        pass

    def filter_packets(self, packets):
        '''Remove any expected packets. Whatever is left is considered a leak. Derived classes can
        override this to focus on detecting specific types of leaks.'''

        unmatched = self.traffic_filter.filter_traffic(packets, local=True)[1]
        unmatched = self.traffic_filter.filter_traffic(unmatched, link_local=True)[1]
        unmatched = self.traffic_filter.filter_traffic(unmatched, multicast=True)[1]
        unmatched = self.traffic_filter.filter_traffic(
            unmatched, dst_ip=[self.initial_vpn_server_ip])[1]

        # Ignore VPN traffic. This can happen as some apps retry different server IPs when they
        # try to reconnect. This isn't a leak.
        for vpn_pname in ["openvpn"]:
            unmatched = self.traffic_filter.filter_traffic(unmatched, pname=vpn_pname)[1]

        if self.final_vpn_server_ip:
            unmatched = self.traffic_filter.filter_traffic(
                unmatched, dst_ip=[self.final_vpn_server_ip])[1]

        return unmatched

    def test(self):
        L.describe('Open and connect the VPN application')
        self.localhost['vpn_application'].open_and_connect()

        L.describe('Determine the VPN server IP')
        self.initial_vpn_server_ip = self.localhost['vpn_application'].vpn_server_ip()
        L.info("VPN server IP is {}".format(self.initial_vpn_server_ip))

        L.describe('Capture traffic')
        self.capture_device['packet_capturer'].start()

        # Derived classes *may* generate traffic during the test
        self.start_traffic_generation()

        # Derived classes do whatever they want. The aim is to try to generate a leak. We'll check
        # afterwards whether anything leaked.
        self.test_with_packet_capture()

        check_period = self.parameters.get(
            'check_period', LocalPacketCaptureTestCase.DEFAULT_CHECK_PERIOD)

        if check_period:
            L.describe("Wait {} seconds before stopping traffic capture".format(check_period))

            timeup = TimeUp(check_period)
            while not timeup:
                L.info("Capturing traffic for another {} seconds".format(
                    math.ceil(timeup.time_left())))
                time.sleep(5)

        # Stop traffic generation
        self.stop_traffic_generation()

        # If tests disrupt the VPN then the VPN server IP can change. We don't class traffic to
        # this IP as a leak so we want to filter that out as well.
        self.final_vpn_server_ip = self.localhost['vpn_application'].vpn_server_ip()
        if self.final_vpn_server_ip and self.initial_vpn_server_ip != self.final_vpn_server_ip:
            L.info(
                "VPN server IP changed during testing to {}. This isn't a problem and is "
                "expected in many test cases".format(self.final_vpn_server_ip))

        L.describe('Stop capturing traffic')
        packets = self.capture_device['packet_capturer'].stop()
        packets = self.filter_packets(packets)

        self.assertEmpty(
            packets, "Found the following leaked packets:\n{}".format(Packets(packets)))
