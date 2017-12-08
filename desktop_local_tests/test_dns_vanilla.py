from desktop_local_tests.dns_helper import DNSHelper
from desktop_local_tests.local_test_case import LocalTestCase
from xv_leak_tools.log import L

class TestDNSVanilla(LocalTestCase):
    '''Summary:

    Test whether DNS leaks during regular VPN connection.

    Details:

    This test will first ask the system for all known DNS servers. It will then connect to
    the VPN and do a DNS lookup. It asserts that the server used for the DNS lookup was not one
    which was known to the system before connecting to the VPN and that it was also one of the VPN
    server IPs. There is redundancy in this check but no harm.

    Discussion:

    This test is a quick smoke test to catch obvious DNS leaks. If a provider fails this test then
    they will almost certainly fail all other DNS tests.

    Weaknesses:

    * A single test of DNS lookup will not hit every DNS server known to the system. Potentially
      this can mask leaks. The test TestDNSVanillaAggressive is designed to remedy this.

    Scenarios:

    * Run on a system with DNS servers configured to be public IP addresses, e.g. 8.8.8.8.
    * Run on a system with DNS servers configured to be local IP addresses, e.g. 192.0.0.0/24. This
      is a common setup with home routers where the router acts as the DNS server.

    TODO:

    * For VPN providers which use a public IP for their DNS server, rather than the tunnel IP, test
      whether they leak DNS requests to other public IPs.
    '''

    def test(self):
        L.describe('Find all known DNS servers before connecting to VPN')
        dns_servers_before_connect = self.localhost['dns_tool'].known_servers()
        L.info("All known DNS servers are: {}".format(dns_servers_before_connect))

        L.describe('Open and connect the VPN application')
        self.localhost['vpn_application'].open_and_connect()

        vpn_dns_servers = self.localhost['vpn_application'].dns_server_ips()
        L.info("VPN DNS servers are: {}".format(vpn_dns_servers))

        L.describe('Check DNS server used was a VPN DNS server')
        DNSHelper(self.localhost['dns_tool']).dns_server_is_vpn_server(
            dns_servers_before_connect, vpn_dns_servers)
