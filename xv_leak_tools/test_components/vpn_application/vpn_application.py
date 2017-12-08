import ipaddress

from xv_leak_tools.exception import XVEx
from xv_leak_tools.log import L
from xv_leak_tools.manual_input import message_and_await_enter, message_and_await_string, message_and_await_yes_no
from xv_leak_tools.test_components.component import Component

class VPNApplication(Component):

    # pylint: disable=no-self-use

    def __init__(self, device, config):
        super().__init__(device, config)
        self._connected = True

    def _get_ips(self, msg, max_ips=0):
        msg = msg + " Press enter after each one. When finished, just press enter."
        ips = []
        while 1:
            ip_string = message_and_await_string(msg)
            if not ip_string:
                break
            try:
                ips.append(ipaddress.ip_address(ip_string))
                if max_ips != 0 and len(ips) == max_ips:
                    break
            except (ipaddress.AddressValueError, ValueError) as ex:
                L.warning("{}: invalid IP address. Please re-enter.".format(ex))

        if not ips:
            L.warning('User did not provide any valid IP addresses')
        return ips

    def open(self):
        # No point telling the user to do this. If we're going to be doing manual steps anyway then
        # let's just ask them to connect
        pass

    def close(self):
        message_and_await_enter('Close the VPN application')

    def disconnect(self):
        message_and_await_enter('Disconnect from the VPN')

    def connect(self):
        message_and_await_enter('Connect to the VPN')

    def check_configuration(self, config):
        message_and_await_yes_no("Is the VPN application configured as follows:\n{}".format(config))

    def wait_for_connection_interrupt_detection(self, timeout=65): # pylint: disable=unused-argument
        # TODO: Add timeout to message_and_await_enter?
        message_and_await_enter(
            'Wait for the VPN application to detect a connection disruption then press enter')

    def configure(self):
        skip_settings = self._config.get('skip_settings', True)
        settings = self._config.get('settings', {})
        human_readable = settings.get('human_readable', None)

        if human_readable is not None:
            L.describe("VPN application should be configured to {}".format(human_readable))
        elif settings:
            L.describe("VPN application should be configured to {}".format(settings))

        if not settings:
            L.warning("No settings specified for VPN application. Using current settings.")
            return
        elif skip_settings:
            L.warning("Configuring VPN application skipped as skip_settings=True")
            return

        msg = ""
        for key, value in list(settings.items()):
            msg += "  {} => {}\n".format(key, value)

        message_and_await_enter(
            "Configure the VPN application with the following settings:\n{}".format(msg))

    def preferences(self):
        L.warning("Can't automatically determine preferences for this VPN application")
        return {}

    def tunnel_interface(self):
        return message_and_await_string(
            'Please input the tunnel interface for the VPN or leave blank if unknown')

    def vpn_processes(self):
        # TODO: Anything we can do?
        L.warning("Can't automatically determine the VPN processes for this VPN application")
        return []

    def vpn_server_ip(self):
        ips = self._get_ips('Please input the VPN server IP.', max_ips=1)
        if len(ips) > 1:
            raise XVEx('User provided more than one VPN server IP')
        if ips:
            return ips[0]
        return None

    def dns_server_ips(self):
        return self._get_ips('Please input the DNS server IPs you expect the VPN app to use.')

    def tunnel_gateway(self):
        return self._get_ips('Please input the tunnel gateway IP.')

    def connection_state(self):
        # TODO: Think more carefully about states. They are quite "ExpressVPNy" at the moment.
        return 'connected' if self._connected else 'ready'

    def protocol(self):
        # TODO: Change to a list of choices
        return message_and_await_string('Please input the VPN protocol or leave blank if unknown')

    # Convenience method
    def open_and_connect(self):
        self.open()
        self.connect()
