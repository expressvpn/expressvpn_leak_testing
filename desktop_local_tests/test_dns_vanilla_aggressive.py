import random

from multiprocessing.pool import ThreadPool

from desktop_local_tests.dns_helper import DNSHelper
from desktop_local_tests.local_test_case import LocalTestCase
from xv_leak_tools.exception import XVEx
from xv_leak_tools.log import L

class TestDNSVanillaAggressive(LocalTestCase):

    '''Summary:

    Test whether DNS leaks during regular VPN connection.

    Details:

    This test will first ask the system for all known DNS servers. It will then connect to the VPN
    and perform multiple DNS requests in parallel. It asserts that the server used for the DNS
    lookup was not one which was known to the system before connecting to the VPN and that it was
    also one of the VPN server IPs. There is redundancy in this check but no harm.

    Discussion:

    The test is very similar to TestDNSVanilla but just performs multiple DNS lookups. Most
    providers should pass this test. The

    Weaknesses:

    Currently uses dig to decide if DNS leaks. This isn't reliable for some VPN providers. Some
    providers intercept DNS upstream and change the destination DNS server to their own server.
    However dig will still report the server which it originally sent the request to.

    Scenarios:

    * Run on a system with DNS servers configured to be public IP addresses, e.g. 8.8.8.8.
    * Run on a system with DNS servers configured to be local IP addresses, e.g. 192.0.0.0/24. This
      is a common setup with home routers where the router acts as the DNS server.
    '''

    # TODO: Potentially make configurable
    HOSTNAMES = [
        'google.com', 'twitter.com', 'facebook.com', 'stackoverflow.com', 'yahoo.com', 'amazon.com',
    ]

    # TODO: Potentially make configurable
    NUMBER_OF_DNS_REQUESTS = 50

    def __init__(self, devices, parameters):
        super().__init__(devices, parameters)
        self.dns_servers_before_connect = []
        self.vpn_dns_servers = []
        self.dns_helper = DNSHelper(self.localhost['dns_tool'])
        self.thread_pool = ThreadPool(processes=10)

    def dns_server_known(self, hostname):
        server = self.localhost['dns_tool'].lookup(hostname)[0]

        self.assertIsIn(
            server, self.dns_servers_before_connect,
            "DNS server used was {} but that wasn't known to the system".format(server))

    def dns_server_is_vpn_dns(self, hostname):
        self.dns_helper.dns_server_is_vpn_server(
            self.dns_servers_before_connect, self.vpn_dns_servers, hostname=hostname)

    def check_multiple_asynchronously(self, func):
        results = []
        # TODO: Think about what else we could do here. More domains? Different methods of DNS
        # lookup?
        for _ in range(0, TestDNSVanillaAggressive.NUMBER_OF_DNS_REQUESTS):
            # Warning: If you miss the trailing comma in the args to the func passed to apply_async
            # then the string will be interpreted as an array of arguments!
            results.append(self.thread_pool.apply_async(
                func, (random.choice(TestDNSVanillaAggressive.HOSTNAMES),)))

        # There is no result returned from check_dns, but .get() will propagate any exception
        # thrown by check_dns, which is what we want.
        first_exception = None
        for result in results:
            try:
                result.get()
            except XVEx as ex:
                if first_exception is None:
                    first_exception = ex

        # pylint: disable=raising-bad-type
        if first_exception is not None:
            raise first_exception

    def test(self):
        L.describe('Find all known DNS servers before connecting to VPN')
        self.dns_servers_before_connect = self.localhost['dns_tool'].known_servers()

        L.info("All known DNS servers are: {}".format(self.dns_servers_before_connect))

        # Sanity check that the DNS servers we initially use are known. This is not strictly part
        # of the test.
        self.check_multiple_asynchronously(self.dns_server_known)

        L.describe('Open and connect the VPN application')
        self.localhost['vpn_application'].open_and_connect()

        self.vpn_dns_servers = self.localhost['vpn_application'].dns_server_ips()
        L.info("VPN DNS servers are: {}".format(self.vpn_dns_servers))

        L.describe(
            "Check DNS server used was a VPN DNS server by doing {} asynchronous DNS "
            "requests".format(TestDNSVanillaAggressive.NUMBER_OF_DNS_REQUESTS))

        self.check_multiple_asynchronously(self.dns_server_is_vpn_dns)
