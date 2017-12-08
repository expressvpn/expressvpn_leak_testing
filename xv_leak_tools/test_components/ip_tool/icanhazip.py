import ipaddress

from xv_leak_tools.exception import XVEx

class ICanHazIP:

    def __init__(self, url_getter):
        self._url_getter = url_getter

    def _get_public_ip_addresses(self, url):
        stdout = self._url_getter(url)[0].strip()
        if stdout == '':
            # No ip addresses. This is okay.
            return []
        try:
            return [ipaddress.ip_address(stdout)]
        except ValueError as _:
            raise XVEx("Couldn't convert output '{}' from {} into an IP".format(stdout, url))

    def public_ipv4_addresses(self):
        return self._get_public_ip_addresses('http://ipv4.icanhazip.com')

    def public_ipv6_addresses(self):
        return self._get_public_ip_addresses('http://ipv6.icanhazip.com')

    def all_public_ip_addresses(self):
        return self.public_ipv4_addresses() + self.public_ipv6_addresses()
