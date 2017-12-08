import ipaddress
from xv_leak_tools.log import L
from xv_leak_tools.exception import XVEx

def is_global_ip(ip):
    if not ip:
        return False
    return ipaddress.ip_address(ip).is_global

def get_vpn_server_ip(capture_data, whitelist=None):
    whitelist = whitelist or []

    capture_data = []
    for packet in capture_data:
        if not (packet['SourceIP'] in whitelist) or (packet['DestIP'] in whitelist):
            continue
        del packet

    capture_data = [x for x in capture_data if is_global_ip(x['DestIP'])]

    # TODO: Filter local multicast traffic.

    # TODO: The below is a hack to drop ICMP packets (probably) destined to
    # our servers. It absolutely has to go, since it changes the expectations
    # we put on traffic -- either we fix the behaviour of our app (?) or move
    # finer-grained control over traffic expectation to the configuration.
    L.warning('ICMP is not considered a leak for now')
    capture_data = [x for x in capture_data if not (x['SourcePort'] == '' and x['DestPort'] == '')]

    if whitelist:
        L.debug('After removing whitelisted packets, {} packets remain'.format(len(capture_data)))

    remote_ips = set([packet['DestIP'] for packet in capture_data])

    if len(remote_ips) == 1:
        ip = ipaddress.ip_address(remote_ips.pop())
        L.info('The VPN server IP address is {}.'.format(ip))
        return ip
    else:
        raise XVEx('No unique remote IP: {}.'.format(", ".join(remote_ips)))

class TrafficAnalyser:

    # pylint: disable=too-few-public-methods

    def __init__(self):
        pass

    @staticmethod
    def get_vpn_server_ip(capture_data, whitelist=None):
        L.debug('Determining the VPN server IP')
        return get_vpn_server_ip(capture_data, whitelist)
