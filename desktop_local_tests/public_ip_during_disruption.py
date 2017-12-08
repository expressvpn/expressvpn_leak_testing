import math

from desktop_local_tests.local_test_case import LocalTestCase
from xv_leak_tools.exception import XVEx
from xv_leak_tools.helpers import TimeUp
from xv_leak_tools.log import L

class PublicIPDuringDisruptionTestCase(LocalTestCase):

    DEFAULT_CHECK_PERIOD = 90

    def __init__(self, disrupter_class, devices, parameters):
        super().__init__(devices, parameters)
        self._check_period = parameters.get(
            'check_period', PublicIPDuringDisruptionTestCase.DEFAULT_CHECK_PERIOD)
        self.disrupter = disrupter_class(self.localhost, self.parameters)

    def setup(self):
        super().setup()
        self.disrupter.setup()

    def test(self):
        L.info("Using disrupter: {}".format(self.disrupter))

        L.describe('Get public IP before connect')
        ipv4_addresses_pre_connect = self.localhost['ip_tool'].public_ipv4_addresses()
        ipv6_addresses_pre_connect = self.localhost['ip_tool'].public_ipv6_addresses()
        ip_addresses_pre_connect = ipv4_addresses_pre_connect + ipv6_addresses_pre_connect

        L.info("Public IP addresses before connection were: {}".format(ip_addresses_pre_connect))

        L.describe('Open and connect the VPN application')
        self.localhost['vpn_application'].open_and_connect()

        L.describe("Create disruption...")
        self.disrupter.create_disruption()

        L.describe(
            "Repeatedly check public IP address for the next {} seconds".format(
                self._check_period))

        timeup = TimeUp(self._check_period)
        message_time = self._check_period
        while not timeup:
            try:
                if timeup.time_left() < message_time:
                    L.info("Running IP tests for another {} seconds".format(
                        math.ceil(timeup.time_left())))
                    message_time = message_time - 5

                # Max timeout for each IP lookup is 1 second. It needs to be quick in order to
                # find disruption windows. This will eventually be replaces by something like iperf
                # but which tracks what IPs packets came from.
                current_ipv4_addresses = self.localhost['ip_tool'].public_ipv4_addresses(timeout=1)
                if len(current_ipv4_addresses) != 0:
                    L.debug("Got IPv4 address {}".format(current_ipv4_addresses[0]))

                    # Let's not check against the VPN server IP as it means prompting for user input
                    # for the VPN IP in many cases

                    self.assertIsNotIn(
                        current_ipv4_addresses[0], ip_addresses_pre_connect,
                        "IPv4 address {} used but this is a public IP of this device".format(
                            current_ipv4_addresses[0]))

                # Do ipv4 and ipv6 separately to reduce lookup time. Only do IPv6 if the device has
                # an ipv6 address else it's a waste of time.
                if len(ipv6_addresses_pre_connect) == 0:
                    continue

                current_ipv6_addresses = self.localhost['ip_tool'].public_ipv6_addresses(timeout=1)
                if len(current_ipv6_addresses) != 0:
                    L.debug("Got IPv6 address {}".format(current_ipv6_addresses[0]))
                    # Let's not check against the VPN server IP as it means prompting for user input
                    # for the VPN IP in many cases
                    self.assertIsNotIn(
                        current_ipv6_addresses[0], ipv6_addresses_pre_connect,
                        "IPv6 address {} used but this is a public IP of this device".format(
                            current_ipv6_addresses[0]))

            except XVEx as ex:
                L.warning("IP lookup failed, assuming timeout: {}".format(ex))

    def teardown(self):
        self.disrupter.teardown()
        super().teardown()
