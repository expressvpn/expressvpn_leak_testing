import os
import ipaddress
import re

from abc import ABCMeta, abstractmethod

from xv_leak_tools.exception import XVEx
from xv_leak_tools.helpers import current_os
from xv_leak_tools.log import L
from xv_leak_tools.network.common import RE_IPV4_ADDRESS
from xv_leak_tools.test_components.vpn_application.vpn_application import VPNApplication

# TODO: Break these helper classes out into separate files
class VPNInfo:

    # pylint: disable=too-few-public-methods

    def __init__(self):
        self.protocol = None
        self.dns_server_ips = []
        self.vpn_processes = []
        self.vpn_server_ip = None
        self.tunnel_interface = None

    def __str__(self):
        return "Protocol: {}, PIDs: {}, DNS: {}, IP: {}, tun: {}".format(
            self.protocol, self.vpn_processes, self.dns_server_ips, self.vpn_server_ip,
            self.tunnel_interface)

class VPNDetector(metaclass=ABCMeta):

    @abstractmethod
    def detect(self):
        return None

# TODO: Implement this properly
class L2TPDetector(VPNDetector):

    # pylint: disable=too-few-public-methods

    def __init__(self, device):
        self._device = device
        self._l2tp_processes_cache = None
        self._command_line_args_cache = None
        self._config_file_cache = None

    def _reset(self):
        self._l2tp_processes_cache = None
        self._command_line_args_cache = None
        self._config_file_cache = None

    def _l2tp_processes(self):
        if self._l2tp_processes_cache:
            return self._l2tp_processes_cache
        self._l2tp_processes_cache = []
        self._l2tp_processes_cache += self._device.pgrep('racoon')
        self._l2tp_processes_cache += self._device.pgrep('pppd')
        return self._l2tp_processes_cache

    def _get_vpn_server_ip(self):
        # TODO: Horrible. Make this platform agnostic
        if self._device.os_name() != "macos":
            return None

        from xv_leak_tools.network.macos.locations_and_services import MacOSNetwork
        return MacOSNetwork.vpn_server_ip()

    def detect(self):
        L.debug("Trying to determine if we're using the l2tp protocol")
        vpn_info = VPNInfo()

        # Assume that no-process definitively means no openvpn
        if not self._l2tp_processes():
            L.debug('Not using l2tp')
            return None

        L.info("Detected l2tp as the current VPN protocol")

        vpn_info.vpn_processes = self._l2tp_processes()
        vpn_info.protocol = 'l2tp'
        # TODO: Do tunnel_interface
        vpn_info.vpn_server_ip = self._get_vpn_server_ip()
        vpn_info.dns_server_ips = []
        vpn_info.tunnel_interface = None

        if vpn_info.vpn_server_ip == ipaddress.ip_address('127.0.0.1'):
            L.warning(
                "Got vpn server IP 127.0.0.1. The app is likely using a proxy. Removing this IP")
            vpn_info.vpn_server_ip = None

        # Prevent anyone who's holding on to this class from using stale data.
        self._reset()
        L.debug("Detected the following info about openvpn: {}".format(vpn_info))
        return vpn_info

# TODO: This is very ad-hoc for now. Some VPNs use Network Extensions to implement their VPN, e.g.
# for IKEv2. Currently haven't found a reliable way to distinguish these VPNs yet so for now they
# are just classes as "network extension" protocols. This will likely need work.
class NEDetector(VPNDetector):

    # pylint: disable=too-few-public-methods

    def __init__(self, device):
        self._device = device
        self._ne_processes_cache = None

    def _ne_processes(self):
        if self._ne_processes_cache:
            return self._ne_processes_cache
        self._ne_processes_cache = []
        self._ne_processes_cache += self._device.pgrep('neagent')
        return self._ne_processes_cache

    def detect(self):
        if current_os() != "macos":
            return None

        L.debug("Trying to determine if we're using a macOS network extension")
        vpn_info = VPNInfo()

        if not self._ne_processes():
            L.debug('Not using a network extension')
            return None

        L.info("Detected a VPN network extension (unknown protocol)")

        vpn_info.vpn_processes = self._ne_processes()
        return vpn_info

class OpenVPNDetector(VPNDetector):

    # pylint: disable=too-few-public-methods

    UDP_TCP = ['udp', 'tcp']
    PROG_ROUTE = re.compile(".*route ({}).*".format(RE_IPV4_ADDRESS))
    PROG_REMOTE = re.compile(".*remote ({}).*".format(RE_IPV4_ADDRESS))

    def __init__(self, device):
        self._device = device
        # TODO: Does pylint complain if we just use _reset here?
        self._openvpn_process_cache = None
        self._command_line_args_cache = None
        self._config_file_cache = None

    def _reset(self):
        self._openvpn_process_cache = None
        self._command_line_args_cache = None
        self._config_file_cache = None

    def _protocol_from_config_file(self):
        L.debug(
            "Trying to determine if openvpn is using UDP or TCP by looking at the config file")
        if not self._config_file():
            L.debug("Couldn't get config file so can't establish which protocol is being used")
            return None

        with open(self._config_file()) as file_:
            for line in file_.readlines():
                for protocol in OpenVPNDetector.UDP_TCP:
                    if protocol in line:
                        L.debug("Detected protocol {} from the config file".format(protocol))
                        return protocol
        L.warning("Couldn't determine openvpn protocol from config file {}".format(
            self._config_file()))
        return None

    def _openvpn_process(self):
        if self._openvpn_process_cache:
            return self._openvpn_process_cache

        openvpn_pids = self._device.pgrep('openvpn')
        if not openvpn_pids:
            return

        # This is a bit of a hack. Some providers are known to spawn two openvpn instances. We only
        # want the parent one which is the one where --config is specified. So if we find more than
        # one the we will let this slide if exactly one of them has --config in it.
        if len(openvpn_pids) != 1:
            good_pids = []
            for pid in openvpn_pids:
                for arg in self._device.command_line_for_pid(pid):
                    if "--config" in arg:
                        good_pids.append(pid)
            if len(good_pids) != 1:
                raise XVEx(
                    "Found {} openvpn processes, expected exactly 1".format(len(openvpn_pids)))
            openvpn_pids = good_pids

        self._openvpn_process_cache = openvpn_pids[0]
        return self._openvpn_process_cache

    def _command_line_args(self):
        if self._command_line_args_cache:
            return self._command_line_args_cache
        # This can throw. Let it! If we know we're using openvpn but can't get the command line then
        # that's a bug.
        self._command_line_args_cache = self._device.command_line_for_pid(self._openvpn_process())

        L.debug("Got command line args: {}".format(self._command_line_args_cache))
        return self._command_line_args_cache

    def _config_file(self):
        if self._config_file_cache:
            return self._config_file_cache

        config_file = self._command_line_arg('--config')
        if not config_file:
            return None

        if os.path.exists(config_file):
            self._config_file_cache = config_file
            L.debug("Got config file {}".format(self._config_file_cache))
            return self._config_file_cache

        # Couldn't find the config file so maybe it's a relative path to --cd
        working_directory = self._command_line_arg('--cd')
        if working_directory:
            config_file = os.path.join(working_directory, self._command_line_arg('--config'))
            if os.path.exists(config_file):
                self._config_file_cache = config_file
                L.debug("Got config file {}".format(self._config_file_cache))
                return self._config_file_cache

        raise XVEx("Found argument --config={} but the config files doesn't exists".format(
            config_file))

    def _protocol(self):
        '''Can return None'''
        if not self._command_line_args():
            L.debug(
                "Couldn't get command line args so can't establish which protocol is being used")
            return None
        L.debug(
            "Trying to determine if openvpn is using UDP or TCP by looking at command line args")
        # See if we can find udp or tcp just in the command line
        for protocol in OpenVPNDetector.UDP_TCP:
            if protocol in ' '.join(self._command_line_args()):
                L.debug("Detected protocol {} from the command line".format(protocol))
                return protocol

        return self._protocol_from_config_file()

    def _command_line_arg(self, arg_name):
        if '--' not in arg_name:
            arg_name = "--{}".format(arg_name)

        for index, command_line_arg in enumerate(self._command_line_args()):
            if arg_name != command_line_arg:
                continue

            # Will die if the option is a boolean (i.e. has no value) and is the last option.
            return self._command_line_args()[index + 1]
        return None

    def _try_vpn_server_ip_from_command_line(self):
        L.debug("Trying to determine the VPN server IP from the command line")
        for arg_name in ['--remote', '--route']:
            value = self._command_line_arg(arg_name)
            if not value:
                continue

            L.debug("Found command line arg {}={}".format(arg_name, value))

            try:
                ipaddress.ip_address(value)
                return value
            except ValueError as ex:
                L.warning("Expected {} to be an the openvpn server IP: {}".format(value, ex))

        L.debug("Couldn't determine VPN server IP from command line {}".format(
            self._command_line_args()))

        return None

    def _try_vpn_server_ip_from_config_file(self):
        L.debug("Trying to determine the VPN server IP from the config file")
        if not self._config_file():
            L.debug("Couldn't get config file so can't determine the VPN server IP")
            return None

        # TODO: DRY
        with open(self._config_file()) as file_:
            for line in file_.readlines():
                match = OpenVPNDetector.PROG_REMOTE.match(line)
                if match:
                    ip = match.group(1)
                    L.debug("Got VPN server IP {} from the --remote".format(ip))
                    return ip
                match = OpenVPNDetector.PROG_ROUTE.match(line)
                if match:
                    ip = match.group(1)
                    L.debug("Got VPN server IP {} from the --route".format(ip))
                    return ip
        L.debug("Couldn't determine VPN server IP from config file {}".format(self._config_file()))
        return None

    def _vpn_server_ip(self):
        if not self._command_line_args():
            L.debug("Couldn't get command line args so can't determine the VPN server IP")
            return None
        ip = self._try_vpn_server_ip_from_command_line()
        if ip:
            return ipaddress.ip_address(ip)
        ip = self._try_vpn_server_ip_from_config_file()
        if ip:
            return ipaddress.ip_address(ip)

        return None

    def _log_file(self):
        if not self._command_line_args():
            return None
        return self._command_line_arg('--log')

    def _dns_server_ips(self):
        log_file = self._log_file()
        if not log_file:
            return None

        L.debug("Searching for DHCP in openvpn log file: {}".format(log_file))
        # It's perfectly possible for one line to have this many times, e.g.
        # PUSH_REPLY,redirect-gateway def1 bypass-dhcp,dhcp-option DNS 1.2.3.4,
        # dhcp-option DNS 5.6.7.8
        prog = re.compile("dhcp-option DNS ({})".format(RE_IPV4_ADDRESS))
        with open(log_file) as file_:
            for line in reversed(file_.readlines()):
                matches = prog.findall(line)
                if not matches:
                    continue
                ips = []
                for match in matches:
                    ips.append(ipaddress.ip_address(match))
                return ips

        return None

    def detect(self):
        L.debug("Trying to determine if we're using the openvpn protocol")
        vpn_info = VPNInfo()

        # Assume that no-process definitively means no openvpn
        if not self._openvpn_process():
            L.debug("There are no openvpn processes so we can't be using openvpn")
            return None

        L.info("Detected openvpn as the current VPN protocol")

        vpn_info.vpn_processes = [self._openvpn_process()]
        vpn_info.protocol = self._protocol()
        vpn_info.vpn_server_ip = self._vpn_server_ip()
        vpn_info.dns_server_ips = self._dns_server_ips()
        # TODO: Do tunnel_interface
        vpn_info.tunnel_interface = None

        if vpn_info.vpn_server_ip == ipaddress.ip_address('127.0.0.1'):
            L.warning(
                "Got vpn server IP 127.0.0.1. The app is likely using a proxy. Removing this IP")
            vpn_info.vpn_server_ip = None

        # Prevent anyone who's holding on to this class from using stale data.
        self._reset()
        L.debug("Detected the following info about openvpn: {}".format(vpn_info))
        return vpn_info

# Override methods here where we can "guess" info about the VPN
class DesktopVPNApplication(VPNApplication):

    def __init__(self, app_path, device, config):
        super().__init__(device, config)
        self._app_path = app_path
        self._vpn_detectors = [
            OpenVPNDetector(self._device),
            L2TPDetector(self._device),
            NEDetector(self._device),
        ]
        self._routes_before_connect = None

    def _vpn_server_ip_from_route(self):
        L.debug("Attempting to get VPN server IP from routing table")
        routes = self._device['route'].get_v4_routes()
        if not routes or not self._routes_before_connect:
            return None

        potential_routes = []
        for route in routes:
            if route in self._routes_before_connect:
                continue
            dest_ip = route.destination_ip()
            if dest_ip and route.gateway_ip() and not dest_ip.is_private:
                potential_routes.append(route)

        if len(potential_routes) == 1:
            ip = potential_routes[0].destination_ip()
            L.debug("Got VPN server IP {} from routing table".format(ip))
            return ip
        elif len(potential_routes) >= 1:
            L.warning(
                "Tried to get VPN server from route table but found more than one "
                "candidate:\n{}".format(potential_routes))
        else:
            L.warning("Couldn't find any routes which look like they're for the VPN server")

        return None

    def open(self):
        if self._app_path:
            L.info("Opening VPN application {} (it might take a moment to appear)".format(
                self._config["name"]))
            self._device.open_app(self._app_path)
        else:
            super().open()

    def close(self):
        if self._app_path:
            L.info("Closing VPN app: {}".format(self._app_path))
            self._device.close_app(self._app_path)
        else:
            super().close()

    def connect(self):
        self._routes_before_connect = self._device['route'].get_v4_routes()
        super().connect()

    def disconnect(self):
        super().disconnect()
        self._routes_before_connect = None

    def _vpn_info(self):
        for detector in self._vpn_detectors:
            info = detector.detect()
            if info is not None:
                return info
        return None

    def protocol(self):
        info = self._vpn_info()
        if info is not None and info.protocol:
            return info.protocol

        L.warning("Couldn't determine the VPN protocol. Will fallback to default method")
        return super().protocol()

    def vpn_processes(self):
        info = self._vpn_info()
        if info is not None and info.vpn_processes:
            return info.vpn_processes

        L.warning("Couldn't find VPN processes. Will fallback to default method")
        return super().vpn_processes()

    def vpn_server_ip(self):
        info = self._vpn_info()
        if info is not None and info.vpn_server_ip:
            return info.vpn_server_ip

        ip = self._vpn_server_ip_from_route()
        if ip:
            return ip

        L.warning("Couldn't find VPN server IP. Will fallback to default method")
        return super().vpn_server_ip()

    def dns_server_ips(self):
        info = self._vpn_info()
        if info is not None and info.dns_server_ips:
            return info.dns_server_ips

        L.warning("Couldn't find VPN DNS server IPs. Will fallback to default method")
        return super().dns_server_ips()
