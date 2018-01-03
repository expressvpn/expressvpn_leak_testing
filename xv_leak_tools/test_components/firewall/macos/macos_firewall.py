from xv_leak_tools.log import L
from xv_leak_tools.test_components.firewall.firewall import Firewall

class MacOSFirewall(Firewall):

    def __init__(self, device, config):
        super().__init__(device, config)
        self._pfctl = None
        self._current_rules = []

    @staticmethod
    def _block_ip_rules(ip):
        return [
            "block in quick from {} no state".format(ip),
            "block out quick to {} no state".format(ip)
        ]

    def block_ip(self, ip):
        from xv_leak_tools.network.macos.pf_firewall import PFCtl
        L.info("Adding outgoing IP block for {}".format(ip))

        # Delay initialize the PFCtl object to prevent VPN application connect from removing our
        # reference to the pf firewall. Some VPN apps take full ownership of the firewall which can
        # mean that the firewall will be disabled unless we initialize here.
        if self._pfctl == None:
            self._pfctl = PFCtl()

        self._current_rules += MacOSFirewall._block_ip_rules(ip)
        self._pfctl.set_rules(self._current_rules)

    def unblock_ip(self, ip):
        if self._pfctl is None:
            return

        rules_to_remove = self._block_ip_rules(ip)
        for rule_to_remove in rules_to_remove:
            self._current_rules = [rule for rule in self._current_rules if rule != rule_to_remove]
        self._pfctl.set_rules(self._current_rules)
