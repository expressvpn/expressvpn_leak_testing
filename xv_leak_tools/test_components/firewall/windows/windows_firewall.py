from xv_leak_tools.log import L
from xv_leak_tools.exception import XVEx
from xv_leak_tools.test_components.firewall.firewall import Firewall

class WindowsFirewall(Firewall):

    def __init__(self, device, config):
        super().__init__(device, config)

        from xv_leak_tools.network.windows.adv_firewall import WindowsAdvFirewall
        self._adv_firewall = WindowsAdvFirewall
        self._rule_name = None

    def block_ip(self, ip):
        if self._rule_name is not None:
            raise XVEx("Already added block IP rule to firewall!")
        L.info("Adding outgoing IP block for {}".format(ip))
        self._rule_name = self._adv_firewall.block_ip(ip)

    def unblock_ip(self):
        if self._rule_name is not None:
            self._adv_firewall.delete_rule(self._rule_name)
            self._rule_name = None
