import math

from xv_leak_tools.exception import XVEx
from xv_leak_tools.helpers import TimeUp
from xv_leak_tools.log import L
from desktop_local_tests.dns_helper import DNSHelper
from desktop_local_tests.local_test_case import LocalTestCase

class DNSDuringDisruptionTestCase(LocalTestCase):

    DEFAULT_CHECK_PERIOD = 60

    def __init__(self, disrupter_class, devices, parameters):
        super().__init__(devices, parameters)
        self.dns_helper = DNSHelper(self.localhost['dns_tool'])
        self._check_period = parameters.get(
            'check_period', DNSDuringDisruptionTestCase.DEFAULT_CHECK_PERIOD)
        self.disrupter = disrupter_class(self.localhost, self.parameters)

    def setup(self):
        super().setup()
        self.disrupter.setup()

    def test(self):
        L.info("Using disrupter: {}".format(self.disrupter))

        L.describe('Find all known DNS servers before connecting to VPN')
        dns_servers_before_connect = self.localhost['dns_tool'].known_servers()

        L.info("All known DNS servers are: {}".format(dns_servers_before_connect))

        L.describe('Open and connect the VPN application')
        self.localhost['vpn_application'].open_and_connect()

        vpn_dns_servers = self.localhost['vpn_application'].dns_server_ips()
        L.info("VPN DNS servers are: {}".format(vpn_dns_servers))

        self._check_network(time_limit=20)

        L.describe('Check DNS server used was a VPN DNS server')
        self.dns_helper.dns_server_is_vpn_server(dns_servers_before_connect, vpn_dns_servers)

        L.describe("Create disruption...")
        self.disrupter.create_disruption()

        L.describe(
            "Do some DNS lookups for the next {} seconds and check the DNS server used is a VPN "
            "DNS Server".format(self._check_period))

        timeup = TimeUp(self._check_period)
        message_time = self._check_period
        while not timeup:
            if timeup.time_left() < message_time:
                L.info("Doing DNS lookup tests for another {} seconds".format(
                    math.ceil(timeup.time_left())))
                message_time = message_time - 5

            try:
                # Max timeout for each DNS lookup is 2 seconds.
                timeout = min(timeup.time_left(), 2)
                self.dns_helper.dns_server_is_vpn_server(
                    dns_servers_before_connect, vpn_dns_servers, timeout=timeout)

            except XVEx as ex:
                L.warning("DNS lookup failed, assuming no leak: {}".format(ex))

    def teardown(self):
        self.disrupter.teardown()
        super().teardown()
