from xv_leak_tools.log import L
from xv_leak_tools.test_components.firewall.firewall import Firewall

class MacOSFirewall(Firewall):

    def __init__(self, device, config):
        super().__init__(device, config)
        self._pfctl = None

    def block_ip(self, ip):
        from xv_leak_tools.network.macos.pf_firewall import PFCtl

        # Delay initialize the PFCtl object to prevent VPN application connect from removing our
        # reference to the pf firewall. Some VPN apps take full ownership of the firewall which can
        # mean that the firewall will be disabled unless we initialize here.
        self._pfctl = PFCtl()
        L.info("Adding outgoing IP block for {}".format(ip))
        self._pfctl.set_leak_test_rules(
            [
                "block in quick from {} no state".format(ip),
                "block out quick to {} no state".format(ip)
            ])

    def unblock_ip(self):
        if self._pfctl is not None:
            self._pfctl.clear_leak_test_rules()
