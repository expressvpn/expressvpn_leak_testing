from xv_leak_tools.log import L
from xv_leak_tools.test_components.dns_tool.dns_lookup_tool import DNSLookupTool

class LinuxDNSTool(DNSLookupTool):

    def known_servers(self):
        L.warning(
            'TODO: Implement DNS server discovery for Linux. Currently we just return the DNS '
            'server used for a DNSserver')
        dns_servers = [self.lookup()[0]]
        self._check_current_dns_server_is_known(dns_servers)
        return dns_servers
