import ipaddress
import json

from xv_leak_tools.log import L
from xv_leak_tools.exception import XVEx

class TrafficFilter:

    VALID_RULES = [
        'direction', 'pname', 'pid', 'iface', 'src_ip', 'dst_ip', 'src_port', 'dst_port', 'local',
        'link_local', 'multicast'
    ]

    @staticmethod
    def _create_rules(**kwargs):
        rules = {}
        for key, value in kwargs.items():
            if key not in TrafficFilter.VALID_RULES:
                raise XVEx("Invalid filter rule: {}".format(key))
            L.debug("Adding rule {}: {}".format(key, value))
            rules[key] = value
        return rules

    @staticmethod
    def match(packet, rules):
        for rule, rule_value in list(rules.items()):
            if not getattr(TrafficFilter, "match_{}".format(rule))(packet, rule_value):
                return False
        return True

    @staticmethod
    def match_direction(packet, direction):
        return packet['Direction'] == direction

    @staticmethod
    def match_pname(packet, pname):
        # Slightly looser check here. This helps, for example, in matching openvpn when VPN
        # providers name their own openvpn binary, like someprovider-openvpn
        return pname in packet['Pname']

    @staticmethod
    def match_pid(packet, pid):
        # Stringify just to cater for stray ints making it into this function
        return str(packet['Pid']) == str(pid)

    @staticmethod
    def match_iface(packet, iface):
        return packet['Iface'] == iface

    @staticmethod
    def match_src_ip(packet, src_ips):
        if not isinstance(src_ips, list):
            src_ips = [src_ips]
        return packet['SourceIP'] in src_ips

    @staticmethod
    def match_dst_ip(packet, dst_ips):
        if not isinstance(dst_ips, list):
            dst_ips = [dst_ips]
        return packet['DestIP'] in dst_ips

    @staticmethod
    def match_src_port(packet, src_ports):
        if not isinstance(src_ports, list):
            src_ports = [src_ports]
        src_ports = [str(p) for p in src_ports]
        return str(packet['SourcePort']) in src_ports

    @staticmethod
    def match_dst_port(packet, dst_ports):
        if not isinstance(dst_ports, list):
            dst_ports = [dst_ports]
        dst_ports = [str(p) for p in dst_ports]
        return packet['DestPort'] in dst_ports

    @staticmethod
    def match_local(packet, _):
        return ipaddress.ip_address(packet['DestIP']).is_private

    @staticmethod
    def match_link_local(packet, _):
        return ipaddress.ip_address(packet['DestIP']).is_link_local

    @staticmethod
    def match_multicast(packet, _):
        return ipaddress.ip_address(packet['DestIP']).is_multicast

    @staticmethod
    def filter_traffic(packets, **kwargs):
        def handle_ips(obj):
            if isinstance(obj, (ipaddress.IPv4Address, ipaddress.IPv6Address)):
                return obj.exploded
            return obj

        rules = TrafficFilter._create_rules(**kwargs)

        L.debug("Filtering {} packets against the following rules: {}".format(
            len(packets), json.dumps(rules, indent=2, default=handle_ips)))

        matched, unmatched = [], []
        for packet in packets:
            if TrafficFilter.match(packet, rules):
                matched.append(packet)
            else:
                unmatched.append(packet)

        return matched, unmatched
