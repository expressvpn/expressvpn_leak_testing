import ipaddress
import re

from xv_leak_tools.exception import XVEx

RE_IPV4_ADDRESS = r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}'
PROG_MAC_ADDRESS_COLON = re.compile(
    r"[0-9a-f]{1,2}:[0-9a-f]{1,2}:[0-9a-f]{1,2}:[0-9a-f]{1,2}:[0-9a-f]{1,2}:[0-9a-f]{1,2}")
PROG_MAC_ADDRESS_DOT = re.compile(
    r"[0-9a-f]{1,2}.[0-9a-f]{1,2}.[0-9a-f]{1,2}.[0-9a-f]{1,2}.[0-9a-f]{1,2}.[0-9a-f]{1,2}")

def ips_to_ip_addresses(ips):
    if not isinstance(ips, list):
        return ipaddress.ip_address(ips)

    ret = []
    for ip in ips:
        if isinstance(ip, str):
            ret.append(ipaddress.ip_address(ip))
        elif isinstance(ip, (ipaddress.IPv4Address, ipaddress.IPv6Address)):
            ret.append(ip)
        else:
            raise XVEx("Can't convert {} to an ip address object".format(ip))
    return ret

def ip_addresses_to_strings(ips):
    if not isinstance(ips, list):
        if isinstance(ips, str):
            return ips
        return ips.exploded

    ret = []
    for ip in ips:
        if isinstance(ip, str):
            ret.append(ip)
        elif isinstance(ip, (ipaddress.IPv4Address, ipaddress.IPv6Address)):
            ret.append(ip.exploded)
        else:
            raise XVEx("Can't convert {} to an ip address string".format(ip))
    return ret

def is_mac_address(mac):
    if PROG_MAC_ADDRESS_COLON.match(mac) or PROG_MAC_ADDRESS_DOT.match(mac):
        return True
    return False
