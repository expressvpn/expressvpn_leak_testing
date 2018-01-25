import ipaddress
import re
import time
import netifaces

# We disable wildcard warnings for SystemConfiguration. It has a lot of functions and also they're
# dynamically generated (I believe) so importing them by name confuses pylint in a different way.
# Disabling too-few-public-methods is for _SCUtil class. I'm half expecting this to grow over time
# so no need to refactor yet.
# pylint: disable=wildcard-import,undefined-variable,unused-wildcard-import,too-few-public-methods

from SystemConfiguration import *

from xv_leak_tools.exception import XVEx
from xv_leak_tools.log import L
from xv_leak_tools.network.common import RE_IPV4_ADDRESS, ip_addresses_to_strings
from xv_leak_tools.process import XVProcessException, check_subprocess

# The following doc is very useful for understanding how this stuff works
# https://developer.apple.com/library/content/documentation/Networking/Conceptual/SystemConfigFrameworks/SC_UnderstandSchema/SC_UnderstandSchema.html

def _split_dns_servers(servers):
    dns_servers = []
    for line in servers:
        matches = NetworkService.PROG_IPV4.match(line)
        if not matches:
            continue
        dns_servers.append(matches.group(1))
    return dns_servers

class _MacOSNetworkHelper:

    @staticmethod
    def create_preferences():
        return SCPreferencesCreate(None, "xv_leak_tools", None)

    @staticmethod
    def create_dynamic_store():
        return SCDynamicStoreCreate(None, "xv_leak_tools", None, None)

    @staticmethod
    def save_preferences(sc_preferences):
        # TODO: Do I need to commit and apply in all cases
        return SCPreferencesCommitChanges(sc_preferences) and \
            SCPreferencesApplyChanges(sc_preferences)

class _SCUtil:

    PROG_NAMESERVER = re.compile(r".*nameserver\[\d+\] : ({}).*".format(RE_IPV4_ADDRESS))

    @staticmethod
    def _parse_resolver(lines, istart):
        ips = []
        iline = istart
        for iline in range(istart, len(lines)):
            matches = _SCUtil.PROG_NAMESERVER.match(lines[iline])
            if matches:
                ips.append(matches.group(1))
                continue
            if len(lines[iline].strip()) == 0:
                break
        return [ips, iline + 1]

    # Try to parse lines like
    # resolver #3
    #   nameserver[0] : 8.8.8.8
    #   nameserver[1] : 8.8.4.4
    #   if_index : 9 (vlan0)
    #   flags    : Scoped, Request A records, Request AAAA records
    #   reach    : Reachable
    @staticmethod
    def _parse_resolvers(lines):
        ips = []
        iline = 0
        while iline < len(lines):
            if 'resolver #' not in lines[iline]:
                iline += 1
                continue
            new_ips, iline = _SCUtil._parse_resolver(lines, iline + 1)
            ips += new_ips
        return [ipaddress.ip_address(ip) for ip in ips]

    @staticmethod
    def dns_servers_in_priority_order():
        lines = check_subprocess(['scutil', '--dns'])[0].splitlines()
        istart = None
        for iline in range(0, len(lines)):
            if 'DNS configuration (for scoped queries)' in lines[iline]:
                istart = iline + 1
                break

        return list(set(_SCUtil._parse_resolvers(lines[istart:])))

class _NetworkObject:

    def __init__(self, name, id_, sc_preferences):
        self._name = name
        self._id = id_
        self._sc_preferences = sc_preferences

    def __str__(self):
        return "{} ({})".format(self.name(), self.id())

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        return self.id() == other.id()

    def name(self):
        return self._name

    def id(self):
        return self._id

    def _sync_preferences(self):
        SCPreferencesSynchronize(self._sc_preferences)

    def _save_preferences(self):
        return _MacOSNetworkHelper.save_preferences(self._sc_preferences)

class NetworkLocation(_NetworkObject):

    def _cf_set(self):
        return SCNetworkSetCopy(self._sc_preferences, self.id())

    def set_current(self):
        self._sync_preferences()

        if not SCNetworkSetSetCurrent(self._cf_set()) or not self._save_preferences():
            raise XVEx("Couldn't set location '{}' to current location".format(self))

    def current(self):
        return self.id() == SCNetworkSetGetSetID(SCNetworkSetCopyCurrent(self._sc_preferences))

class NetworkService(_NetworkObject):

    # pylint: disable=too-many-public-methods

    TYPE_ETHERNET = 1
    TYPE_WIFI = 2
    TYPE_BRIDGE = 3
    TYPE_VLAN = 4
    TYPE_PPP = 5
    TYPE_VPN = 6
    TYPE_IPSEC = 7

    PROG_IPV4 = re.compile("({})".format(RE_IPV4_ADDRESS))
    PROG_INFO_LINE = re.compile('([^:]+):([^:]+)')

    def _sc_service(self):
        return SCNetworkServiceCopy(self._sc_preferences, self.id())

    def _sc_interface(self):
        return SCNetworkServiceGetInterface(self._sc_service())

    def _ip_addresses(self, key):
        iface = self.interface()
        if iface is None:
            return []

        adds = netifaces.ifaddresses(iface)
        if key not in adds:
            return []
        addrs = [add['addr'].split("%")[0] for add in adds[key]]
        addrs = [ipaddress.ip_address(add) for add in addrs]
        return [add for add in addrs if not add.is_link_local]

    def _ensure_service_is_wifi(self):
        if self.service_type() != NetworkService.TYPE_WIFI:
            raise XVEx("Service {} is not a Wi-Fi service".format(self.name()))

    def _getinfo(self):
        cmd = ['networksetup', '-getinfo', self._name]
        lines = check_subprocess(cmd)[0].splitlines()
        L.verbose("{} returned:\n{}".format(' '.join(cmd), lines))
        info = {}
        for line in lines:
            match = NetworkService.PROG_INFO_LINE.match(line)
            if not match:
                continue
            info[match.group(1).strip()] = match.group(2).strip()
        return info

    def enabled(self):
        return SCNetworkServiceGetEnabled(self._sc_service())

    # TODO: This doesn't work for VPN services
    def active(self):
        if not self.enabled():
            return False
        iface = self.interface()
        if not iface:
            return False

        store = _MacOSNetworkHelper.create_dynamic_store()
        # TODO: This doesn't actually report active correctly
        plist = SCDynamicStoreCopyValue(store, "State:/Network/Interface/{}/Link".format(iface))
        if not plist or 'Active' not in plist:
            L.warning("Can't get link state for {}. Got {}".format(self, plist))
            return False

        if not plist['Active']:
            return False

        ifaces = netifaces.ifaddresses(iface)
        return netifaces.AF_INET in ifaces or netifaces.AF_INET6 in ifaces

    def pingable(self):
        if not self.active():
            return False
        cmd = ['ping', '-c1', '-W1', '8.8.8.8', '-b', self.interface()]
        output = ""
        try:
            output = check_subprocess(cmd)[0]
            if '1 packets received' in output:
                return True
            else:
                # Consider this a real error and propagate. It's likely a code issue.
                raise XVEx("Don't know how to parse ping output: {}".format(output))
        except XVProcessException as ex:
            if 'No route to host' in ex.stderr:
                L.debug("Ping failed due to 'No route to host'")
                return False
            if '0 packets received' in ex.stderr:
                L.debug("Ping failed due to '0 packets received'")
                return False
            L.warning(
                "Ping failed unexpectedly with error '{}'. "
                "Assuming interface un-pingable.".format(ex.stderr))

            return False

    def enable(self):
        L.debug("Enabling network service {}".format(self.name()))
        self._sync_preferences()
        if not SCNetworkServiceSetEnabled(self._sc_service(), True) or not self._save_preferences():
            raise XVEx("Failed to enable network service {}".format(self))

    def enable_ipv6(self):
        # TODO: Try to find a programmatic way of doing this
        check_subprocess(['networksetup', '-setv6automatic', self.name()])

    def disable_ipv6(self):
        # TODO: Try to find a programmatic way of doing this
        check_subprocess(['networksetup', '-setv6off', self.name()])

    def disable(self):
        L.debug("Disabling network service {}".format(self.name()))
        self._sync_preferences()
        if not SCNetworkServiceSetEnabled(self._sc_service(), False) or \
           not self._save_preferences():
            raise XVEx("Failed to disable network service {}".format(self))

    def _sc_dns_servers(self):
        dns_servers = []
        store = _MacOSNetworkHelper.create_dynamic_store()
        # Setup = user configured DNS
        # State = DHCP configured DNS
        for key_type in ["Setup", "State"]:
            plist = SCDynamicStoreCopyValue(store, "{}:/Network/Service/{}/DNS".format(
                key_type, self.id()))

            if not plist or 'ServerAddresses' not in plist:
                continue

            dns_servers += _split_dns_servers(plist['ServerAddresses'])

        return [ipaddress.ip_address(ip) for ip in dns_servers]

    def _ns_dns_servers(self):
        dns_servers = check_subprocess(['networksetup', '-getdnsservers', self._name])
        dns_servers = dns_servers[0].strip().split('\n')
        if "There aren't any DNS Servers set on" in dns_servers[0]:
            return []
        return [ipaddress.ip_address(ip) for ip in dns_servers]

    def dns_servers(self, include_dhcp_servers=True):
        if include_dhcp_servers:
            return self._sc_dns_servers()
        return self._ns_dns_servers()

    def set_dns_servers(self, ips):
        ips = ip_addresses_to_strings(ips)
        L.info('Setting DNS servers for {} to {}'.format(self._name, ips))
        check_subprocess(['networksetup', '-setdnsservers', self._name] + ips)

    def ipv4_addresses(self):
        return self._ip_addresses(netifaces.AF_INET)

    # TODO: Need to note the type of address, e.g.
    # autoconf secured, deprecated autoconf temporary etc.
    def ipv6_addresses(self):
        return self._ip_addresses(netifaces.AF_INET6)

    def interface(self):
        # It's actually possible for a Network Service to report itself as being associated with
        # interface X but interface X no existing!
        all_interfaces = netifaces.interfaces()
        iface = str(SCNetworkInterfaceGetBSDName(self._sc_interface()))
        if iface in all_interfaces:
            return iface
        return None

    def router_ip(self):
        info = self._getinfo()
        if 'Router' not in info:
            return None
        return ipaddress.ip_address(info['Router'])

    # TODO: This is more generic and probably belongs in a posix tool
    def disable_interface(self):
        check_subprocess(['ifconfig', self.interface(), 'down'])

    # TODO: This is more generic and probably belongs in a posix tool
    def enable_interface(self):
        check_subprocess(['ifconfig', self.interface(), 'up'])

    def mac_address(self):
        return str(SCNetworkInterfaceGetHardwareAddressString(self._sc_interface()))

    def remove(self):
        # TODO: Sync and save
        # TODO: Consider making this class invalid now?
        # TODO: Check ret code
        SCNetworkServiceRemove(self._sc_service())

    def service_type(self):
        # pylint: disable=too-many-return-statements

        type_string = self.service_type_string()
        if type_string == "Ethernet":
            return NetworkService.TYPE_ETHERNET
        elif type_string == "Wi-Fi":
            return NetworkService.TYPE_WIFI
        elif type_string == "Bridge":
            return NetworkService.TYPE_BRIDGE
        elif type_string == "VLAN":
            return NetworkService.TYPE_VLAN
        elif type_string == "PPP":
            return NetworkService.TYPE_PPP
        elif type_string == "VPN":
            return NetworkService.TYPE_VPN
        elif type_string == "IPSec":
            return NetworkService.TYPE_IPSEC
        else:
            raise XVEx(
                "Unknown interface type '{}' for network service '{}'".format(type_string, self))

    def service_type_string(self):
        sc_type = SCNetworkInterfaceGetInterfaceType(self._sc_interface())
        if sc_type == "IEEE80211":
            return "Wi-Fi"
        return sc_type

    def _set_wifi_power(self, on_or_off):
        self._ensure_service_is_wifi()
        # TODO: Find a programmatic way of doing this.
        check_subprocess(['networksetup', '-setairportpower', self.interface(), on_or_off])

    def enable_wifi_power(self):
        self._set_wifi_power('On')

    def disable_wifi_power(self):
        self._set_wifi_power('Off')

    def wifi_has_power(self):
        self._ensure_service_is_wifi()

        # TODO: Find a programmatic way of doing this. The data is definitely in
        # /Library/Preferences/SystemConfiguration/preferences.plist
        # but all the Airport keys are deprecated:
        # https://developer.apple.com/documentation/systemconfiguration/scschemadefinitions/airport_dictionary_keys?language=objc
        cmd = ['networksetup', '-getairportpower', self.interface()]
        try:
            output = check_subprocess(cmd)[0]
            if ": Off" in output[0]:
                return False
            elif ": On" in output[0]:
                return True
            else:
                raise XVEx(
                    "Don't know how to parse '{}'' from 'networksetup -getairportpower'".format(
                        output[0]))
        except:
            raise XVEx(
                "Can't get Wi-Fi power status for network service '{}' as it is not a Wi-Fi "
                "service.".format(self))

    def wait_for(self, what, timeout):
        method = getattr(self, what)
        start = time.time()
        okay = method()
        while not okay and time.time() - start < timeout:
            time.sleep(1)
            okay = method()
        if not okay:
            raise XVEx("Network service {} never became {}".format(self, what))
        L.debug("Network service {} became {}".format(self, what))

    # TODO: Really really want to figure out a way to check for connected. I think this has
    # potential to impact tests. e.g. the webrtc one where we renenable the ipv6 service. I've
    # manually verified that in that case it's fine, the service never gets an ipv6 address, but
    # you can visually see the test running before the service went "green"
    def wait_for_active(self, timeout):
        self.wait_for('active', timeout)

    def wait_for_pingable(self, timeout):
        self.wait_for('pingable', timeout)

    def wait_for_ips(self, timeout):
        start = time.time()
        ips = self.ipv4_addresses()
        while not ips and time.time() - start < timeout:
            time.sleep(1)
            ips = self.ipv4_addresses()
        L.debug("Got ips: {}".format(ips))
        if not ips:
            raise XVEx("Network service {} never got lease")

    def renew_dhcp(self):
        # This seems to be the only reliable way to renew the DHCP lease
        self.disable()
        # TODO: Yuck
        time.sleep(0.5)
        self.enable()
        # check_subprocess(['ipconfig', 'set', self.interface(), 'DHCP'])

class MacOSNetwork:

    @staticmethod
    def _sort_services(services, service_order):
        sorted_services = [None] * len(service_order)
        for service in services:
            try:
                sorted_services[service_order.index(service.id())] = service
            except ValueError as _:
                L.warning(
                    "Couldn't determine service order. Couldn't find order for service {}".format(
                        service.name()))

        # It's possible that we had more service order items than services, in which case we strip
        # them. Let's hope it can't be the other way around (presumably we'll have already got an
        # exception in that case!)
        return [service for service in sorted_services if service is not None]

    @staticmethod
    def network_services_in_priority_order():
        preferences = _MacOSNetworkHelper.create_preferences()
        current_set = SCNetworkSetCopyCurrent(preferences)
        sc_services = SCNetworkSetCopyServices(current_set)
        service_order = SCNetworkSetGetServiceOrder(current_set)
        if not sc_services:
            raise XVEx("Failed to get network services when calling SCNetworkServiceCopyAll")

        services = []
        for sc_service in sc_services:
            services.append(NetworkService(
                SCNetworkServiceGetName(sc_service),
                SCNetworkServiceGetServiceID(sc_service),
                preferences))
        return MacOSNetwork._sort_services(services, service_order)

    @staticmethod
    def wifi_service():
        services = MacOSNetwork.network_services_in_priority_order()
        for service in services:
            if service.service_type() == NetworkService.TYPE_WIFI:
                return service
        raise XVEx('There is currently no Wi-Fi service available')

    @staticmethod
    def current_location():
        preferences = _MacOSNetworkHelper.create_preferences()
        sc_set = SCNetworkSetCopyCurrent(preferences)
        return NetworkLocation(
            SCNetworkSetGetName(sc_set),
            SCNetworkSetGetSetID(sc_set),
            preferences)

    @staticmethod
    def network_locations():
        preferences = _MacOSNetworkHelper.create_preferences()
        sc_sets = SCNetworkSetCopyAll(preferences)
        if not sc_sets:
            raise XVEx("Failed to get network locations when calling SCNetworkSetCopyAll")

        locations = []
        for sc_set in sc_sets:
            locations.append(NetworkLocation(
                SCNetworkSetGetName(sc_set),
                SCNetworkSetGetSetID(sc_set),
                preferences))
        return locations

    @staticmethod
    def set_network_service_order(services):
        L.debug("Setting network service order: {}".format(services))
        preferences = _MacOSNetworkHelper.create_preferences()
        current_set = SCNetworkSetCopyCurrent(preferences)
        service_ids = [service.id() for service in services]

        if not SCNetworkSetSetServiceOrder(current_set, service_ids) or \
           not _MacOSNetworkHelper.save_preferences(preferences):
            raise XVEx("Couldn't set network service order for location {}".format(
                SCNetworkSetGetName(current_set)))

    @staticmethod
    def primary_dns_server():
        servers = _SCUtil.dns_servers_in_priority_order()
        return None if len(servers) == 0 else servers[0]

    @staticmethod
    def dns_servers():
        return _SCUtil.dns_servers_in_priority_order()

    @staticmethod
    def vpn_server_ip():
        # TODO: This code is quite hacky. Not sure if it works for anything other than ipsec
        services = MacOSNetwork.network_services_in_priority_order()
        # TODO: This doesn't actually report active correctly. VPN services don't have the link key!
        # services = [service for service in services if service.active()]
        vpn_types = [NetworkService.TYPE_IPSEC, NetworkService.TYPE_PPP, NetworkService.TYPE_VPN]
        for service in services:
            if service.service_type() in vpn_types:
                store = _MacOSNetworkHelper.create_dynamic_store()
                key = "State:/Network/Service/{}/IPv4".format(service.id())
                L.debug("Checking SC store key {} for VPN server IP".format(key))
                plist = SCDynamicStoreCopyValue(store, key)
                if not plist or 'ServerAddress' not in plist:
                    L.debug("Ignoring VPN Service {} as it had no server IP".format(service))
                    continue

                return ipaddress.ip_address(plist['ServerAddress'])
        return None

    @staticmethod
    def up_interfaces():
        ifaces = netifaces.interfaces()
        return [iface for iface in ifaces if netifaces.AF_INET in netifaces.ifaddresses(iface)]
