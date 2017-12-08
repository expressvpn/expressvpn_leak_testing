from xv_leak_tools.test_framework.assertions import Assertions

class DNSHelper(Assertions):

    def __init__(self, dns_tool):
        self._dns_tool = dns_tool

    def dns_server_is_vpn_server(self, dns_servers_before_connect, vpn_dns_servers, **kwargs):
        server = self._dns_tool.lookup(**kwargs)[0]

        # Check DNS server used was not one which was previously known to the system
        # Note that this is overkill as the check below is sufficient, but it's helpful for
        # getting more info.
        self.assertIsNotIn(
            server, dns_servers_before_connect,
            "DNS server used was {} and was known to the system before connect".format(server))

        # Check DNS server used was a VPN DNS server
        self.assertIsIn(
            server, vpn_dns_servers,
            "DNS server used was {} but wasn't a VPN DNS server".format(server))
