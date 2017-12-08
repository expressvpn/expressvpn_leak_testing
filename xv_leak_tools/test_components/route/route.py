import ipaddress

from xv_leak_tools.exception import XVEx
from xv_leak_tools.network.common import is_mac_address
from xv_leak_tools.test_components.local_component import LocalComponent

# pylint: disable=too-few-public-methods

class Route(LocalComponent):
    pass

class RouteFlags:

    # pylint: disable=bad-whitespace

    FLAG_UP                  = 1 << 0
    FLAG_INTERFACE_SCOPED    = 1 << 1
    FLAG_GATEWAY             = 1 << 2
    FLAG_HOST                = 1 << 3
    FLAG_STATIC              = 1 << 4
    FLAG_CLONING             = 1 << 5

    FLAGS_TYPES = {
        "U": FLAG_UP,
        "I": FLAG_INTERFACE_SCOPED,
        "G": FLAG_GATEWAY,
        "H": FLAG_HOST,
        "S": FLAG_STATIC,
        "C": FLAG_CLONING,
    }

    def __init__(self, flags):
        self._raw = flags
        self._bitmask = RouteFlags._parse_flags(flags)

    @staticmethod
    def _parse_flags(flags):
        bitmask = 0
        for flag in flags:
            bitmask |= RouteFlags.FLAGS_TYPES.get(flag, 0)
        return bitmask

    def raw(self):
        return self._raw

class LinkLocalGateway:

    def __init__(self, raw):
        self._raw = raw

    def __str__(self):
        return "linklocal"

    def __repr__(self):
        return self.__str__()

class MacAddress:

    def __init__(self, raw):
        self._raw = raw

    def __str__(self):
        return self._raw

    def __repr__(self):
        return self.__str__()

class RouteEntry:

    DOTS_TO_SUBNET = ["/8", "/16", "/24", ""]

    # pylint: disable=too-many-arguments
    def __init__(self, dest, gway, flags, iface, refs=None, use=None, expire=None, metric=None):
        self._raw = "{}{}{}{}{}{}{}{}".format(dest, gway, flags, refs, use, iface, expire, metric)
        # TODO: Discard quite a few params for now
        self._dest = RouteEntry._parse_dest(dest)
        self._gway = RouteEntry._parse_gway(gway)
        self._iface = iface
        self._flags = RouteFlags(flags)

    def __str__(self):
        return "{} -> {} via {} ({})".format(self._dest, self._gway, self._iface, self._flags.raw())

    def __repr__(self):
        return self.__str__()

    def __eq__(self, rhs):
        # pylint: disable=protected-access
        return self._raw == rhs._raw

    def __hash__(self):
        return self._raw

    @staticmethod
    def _parse_dest(dest):
        if dest == "default":
            return ipaddress.ip_network("0.0.0.0")

        dots = dest.count('.')
        if dots != 3:
            if "/" in dest:
                ip, net = dest.split("/")
                net = "/" + net
            else:
                ip = dest
                net = ""
            for _ in reversed(range(0, 3 - dots)):
                # if i == 0:
                #     dest += ".1"
                # else:
                ip += ".0"
            if "/" not in dest:
                ip += RouteEntry.DOTS_TO_SUBNET[dots]
            dest = ip + net

        return ipaddress.ip_network(dest)

    @staticmethod
    def _parse_gway(gway):
        try:
            return ipaddress.ip_address(gway)
        except ValueError:
            pass

        if 'link' in gway:
            return LinkLocalGateway(gway)

        if is_mac_address(gway):
            return MacAddress(gway)

        raise XVEx("Can't parse route gateway: '{}'".format(gway))

    def destination_ip(self):
        if not self._dest.prefixlen == 32:
            return None
        return self._dest.network_address

    def gateway_ip(self):
        if not isinstance(self._gway, (ipaddress.IPv4Address, ipaddress.IPv6Address)):
            return None
        return self._gway
