import ipaddress

from xml.etree.ElementTree import fromstring

from xv_leak_tools.log import L
from xv_leak_tools.test_components.dns_tool.dns_lookup_tool import DNSLookupTool
from xv_leak_tools.test_device.connector_helper import ConnectorHelper

# N.B. This component *can* run remotely!
class WindowsDNSTool(DNSLookupTool):

    def __init__(self, device, config):
        super().__init__(device, config)
        self._connector_helper = ConnectorHelper(self._device)

    def known_servers(self):
        output = self._connector_helper.check_command([
            'wmic.exe', 'nicconfig', 'where', '"IPEnabled  = True"', 'get', 'DNSServerSearchOrder',
            '/format:rawxml'
        ])[0]

        L.verbose("Got raw wmic output: {}".format(output))
        dns_servers = []
        for nic in fromstring(output).findall("./RESULTS/CIM/INSTANCE"):

            for prop in nic:
                if prop.tag != 'PROPERTY.ARRAY':
                    continue
                for val in prop.findall("./VALUE.ARRAY/VALUE"):
                    ip = ipaddress.ip_address(val.text)
                    dns_servers.append(ip)

        self._check_current_dns_server_is_known(dns_servers)
        return dns_servers
