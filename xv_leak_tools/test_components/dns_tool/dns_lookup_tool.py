import ipaddress

from abc import ABCMeta, abstractmethod

from xv_leak_tools.exception import XVEx
from xv_leak_tools.log import L
from xv_leak_tools.test_components.local_component import LocalComponent
from xv_leak_tools.test_components.dns_tool.dig import Dig

# TODO: This only needs to be LocalComponent because derived classes are. We should restructure
class DNSLookupTool(LocalComponent, metaclass=ABCMeta): # pylint: disable=no-self-use

    DEFAULT_HOSTNAME = 'google.com'
    DEFAULT_TIMEOUT = 5

    def __init__(self, device, config):
        super().__init__(device, config)
        # The separation of Dig and DNSLookupTool is here to easily allow us to add new tools for
        # doing the lookup. We could check the config and see what type of lookup tool we want, e.g.
        # dig, nslookup and so forth.
        self._dig = Dig(self._device)

    def _check_current_dns_server_is_known(self, servers):
        '''This function should be called by known_servers. It does a DNS request and checks that
        the server used is in the list of known servers. This is a sanity check for tests. Many
        tests were doing this themselves. There's no harm in doing it. Consider it a consistency
        check.'''
        server = ipaddress.ip_address(self.lookup()[0])
        if server not in servers:
            raise XVEx("Current DNS server is {} but the system only knows about {}".format(
                server, servers))

    @abstractmethod
    def known_servers(self):
        pass

    # Return server and ips
    def lookup(self, hostname=None, timeout=None, server=None):
        if hostname is None:
            hostname = DNSLookupTool.DEFAULT_HOSTNAME

        if timeout is None:
            timeout = DNSLookupTool.DEFAULT_TIMEOUT

        L.debug("Doing DNS lookup for '{}'".format(hostname))
        server, ips = self._dig.lookup(hostname, timeout, server)
        L.debug("DNS lookup returned ips: {} using server {}".format(ips, server))
        return server, ips
