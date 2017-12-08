import ctypes
import netifaces
import NetworkManager # pylint: disable=import-error

from xv_leak_tools.exception import XVEx
from xv_leak_tools.log import L
from xv_leak_tools.process import check_subprocess

class _NetworkObject:

    def __init__(self, conn):
        self._settings = conn.GetSettings()
        self._id = self._settings['connection']['id']
        self._uuid = self._settings['connection']['uuid']

    def __str__(self):
        return "{} ({})".format(self.id(), self.uuid())

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        return self.uuid() == other.uuid()

    def uuid(self):
        return self._uuid

    def id(self):
        return self._id

    def name(self):
        # TODO: Decide on this API.
        return self._id

class NetworkService(_NetworkObject):

    def active(self):
        active_conns = NetworkManager.NetworkManager.ActiveConnections
        active_conns = [NetworkService(conn.Connection) for conn in active_conns]
        if self in active_conns:
            return True
        return False

    def enable(self):
        L.debug("Enabling connection {}".format(self.name()))
        check_subprocess(['nmcli', 'connection', 'up', self.name()])

    def disable(self):
        L.debug("Disabling connection {}".format(self.name()))
        check_subprocess(['nmcli', 'connection', 'down', self.name()])

    def interface(self):
        # TODO: Reject this idea? Maybe interfaces should be chosen without
        # regard to connection status, if NM can't be trusted.
        # In which case, tests that get a list of interfaces should just use
        # netifaces directly.
        try:
            return self._settings['connection']['interface-name']
        except KeyError:
            connection_type = self._settings['connection']['type']
            # TODO: Test this on different types.
            mac_address = self._settings[connection_type]['mac-address']
            for iface in netifaces.interfaces():
                iface_mac = netifaces.ifaddresses(iface)[netifaces.AF_LINK][0]['addr'].lower()
                if mac_address.lower() == iface_mac:
                    return iface
        raise XVEx("Couldn't find any connection interfaces")

    def enable_interface(self):
        L.debug("Enabling interface {}".format(self.interface()))
        # TODO: Move to unix tools or use "ip link set dev iface up"?
        check_subprocess(['ifconfig', self.interface(), 'up'])

    def disable_interface(self):
        L.debug("Disabling interface {}".format(self.interface()))
        # TODO: Move to unix tools or use "ip link set dev iface up"?
        check_subprocess(['ifconfig', self.interface(), 'down'])

class LinuxNetwork:

    @staticmethod
    def network_services_in_priority_order():
        conns = NetworkManager.Settings.ListConnections()
        conns = list(
            filter(lambda x: 'autoconnect-priority' in x.GetSettings()['connection'], conns))

        # NetworkManager uses int32s so we need to "cast" the autoconnect-priority value.
        def uint32(signed_integer):
            return int(ctypes.c_uint32(signed_integer).value)

        conns.sort(
            key=lambda x: uint32(x.GetSettings()['connection']['autoconnect-priority']),
            reverse=True)

        return [NetworkService(conn) for conn in conns]
