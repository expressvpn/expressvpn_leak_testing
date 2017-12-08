import re

from xv_leak_tools.exception import XVEx
from xv_leak_tools.network.common import RE_IPV4_ADDRESS
from xv_leak_tools.network.macos.locations_and_services import MacOSNetwork

# TODO: MAKE THE dns component do this

# TODO: Make private? How can I do this if I'm importing *?
def parse_ns_lookup_output(lines):
    server = None
    prog = re.compile(r"Server:\s*({})\s*".format(RE_IPV4_ADDRESS))
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
    for service in MacOSNetwork.network_services_in_priority_order():
        possible_dns_servers += service.dns_servers()
    return list(set(possible_dns_servers))
