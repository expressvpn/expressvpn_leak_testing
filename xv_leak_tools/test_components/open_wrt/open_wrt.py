from xv_leak_tools.log import L
from xv_leak_tools.test_components.component import Component
from xv_leak_tools.test_device.shell_connector_helper import ShellConnectorHelper

class OpenWRT(Component):

    def __init__(self, device, config):
        super().__init__(device, config)
        self._connector_helper = ShellConnectorHelper(self._device)

    def _execute(self, cmd):
        return self._connector_helper.check_command(cmd)

    def set_lan_ip(self, ip):
        L.info("Setting LAN IP for router to: {}".format(ip))

        self._connector_helper.check_command(
            ['uci', 'set', "network.lan.ipaddr='{}'".format(ip.exploded)])
        self._connector_helper.check_command(['uci', 'commit', 'network'])
        self._connector_helper.check_command(['/etc/init.d/network', 'restart', '&'])
