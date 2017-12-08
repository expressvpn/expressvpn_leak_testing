import re

from xv_leak_tools.exception import XVEx
from xv_leak_tools.network.common import RE_IPV4_ADDRESS
from xv_leak_tools.network.windows.windows_network import WindowsNetwork

def parse_ns_lookup_output(lines):
    server = None
    prog = re.compile(r"Address:\s*({})\s*".format(RE_IPV4_ADDRESS))
    for line in lines:
        matches = prog.match(line)
        if not matches:
            continue
        server = matches.group(1)
        break

    if server is None:
        raise XVEx("Couldn't parse nslookup output: {}".format(lines))

    # TODO: Implement parsing of actual DNS IPs
    return server, []

def known_dns_servers():
    possible_dns_servers = []
    for adapter in WindowsNetwork.adapters():
        possible_dns_servers += adapter.dns_servers()
    return list(set(possible_dns_servers))
