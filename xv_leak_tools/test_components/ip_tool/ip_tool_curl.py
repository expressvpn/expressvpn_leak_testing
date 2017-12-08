from xv_leak_tools.log import L
from xv_leak_tools.process import XVProcessException
from xv_leak_tools.test_components.local_component import LocalComponent
from xv_leak_tools.test_device.connector_helper import ConnectorHelper
# from xv_leak_tools.test_components.ip_tool.dyndns import DynDNS
from xv_leak_tools.test_components.ip_tool.icanhazip import ICanHazIP

# TODO: Should eventually use our own web server to do these. We rely on 3rd party websites for now
class IPToolCurl(LocalComponent):

    ACCEPTABLE_CURL_ERRORS = [
        "Connection timed out",
        "Couldn't connect to server",
        "Could not resolve host",
        "Resolving timed out after",
        "Operation timed out"
    ]

    def __init__(self, device, config):
        super().__init__(device, config)
        # Separating out DynDNS allows us to easily use hosts to get the IPs if we wish.
        self._dyndns = ICanHazIP(self._curl_url)
        self._connector_helper = ConnectorHelper(device)
        self._max_time = None

    def _execute(self, cmd):
        return self._connector_helper.check_command(cmd)

    def _curl_url(self, url):
        L.debug("Curl-ing url {} to find ips".format(url))
        # TODO: Can't use pycurl on cygwin. Need to figure out how to compile cleanly.
        # try:
        #     L.debug("curl-ing {}".format(url))
        #     curl_instance = curl.Curl(url)
        #     curl_instance.set_option(pycurl.TIMEOUT, 5)
        #     response = curl_instance.get()
        #     print response
        # except pycurl.error as ex:
        #     errno, message = ex.args
        #     if errno == pycurl.E_COULDNT_CONNECT:
        #         L.warning(
        #             "pycurl couldn't connect to {}. Assuming no public IP available.".format(url))
        #         return None
        #     # Be cautious. Haven't assessed what other errors are acceptable so let's
        #     # just raise up
        #     # the error.
        #     raise

        try:

            cmd = ['curl', url, '--connect-timeout', '5']
            if self._max_time:
                cmd += ['-m', self._max_time]
            return self._execute(cmd)
        except XVProcessException as ex:
            for error in IPToolCurl.ACCEPTABLE_CURL_ERRORS:
                if error in ex.stderr:
                    L.verbose(
                        "curl couldn't connect to {}. Assuming no public IP available.".format(url))
                    return "", ""
            # Be cautious. Haven't assessed what other errors are acceptable so let's just raise up
            # the error.
            raise

    def public_ipv4_addresses(self, timeout=None):
        # TODO: Yuck! Redo this class. Hierarchy is bad. Just inherit things like DynDNS from
        # IPToolCurl
        self._max_time = timeout
        return self._dyndns.public_ipv4_addresses()

    def public_ipv6_addresses(self, timeout=None):
        self._max_time = timeout
        return self._dyndns.public_ipv6_addresses()

    def all_public_ip_addresses(self, timeout=None):
        self._max_time = timeout
        return self._dyndns.all_public_ip_addresses()
