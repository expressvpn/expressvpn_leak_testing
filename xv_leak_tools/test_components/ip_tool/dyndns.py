import ipaddress
import re

from xv_leak_tools.log import L

class DynDNS:

    PROG_IPV4 = re.compile(r'.*Current IP Address: ([0-9\.]+).*')
    PROG_IPV6 = re.compile(r'.*Current IP Address: ([0-9a-f\:]+).*')

    def __init__(self, url_getter):
        self._url_getter = url_getter

    def _get_public_ip_addresses(self, url, prog):
        stdout = self._url_getter(url)[0]

        matches = prog.match(stdout)
        if not matches:
            L.warning("Couldn't determine public IP address using {}. Got response\n{}".format(
                url, stdout))
            return []

        return [ipaddress.ip_address(matches.group(1))]

    def public_ipv4_addresses(self):
        return self._get_public_ip_addresses('http://checkip.dyndns.org/', DynDNS.PROG_IPV4)

    def public_ipv6_addresses(self):
        return self._get_public_ip_addresses('http://checkipv6.dyndns.org/', DynDNS.PROG_IPV6)

    def all_public_ip_addresses(self):
        return self.public_ipv4_addresses() + self.public_ipv6_addresses()
