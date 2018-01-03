from xv_leak_tools.log import L
from desktop_local_tests.disrupter import Disrupter

class VPNConnectionDisrupter(Disrupter):

    def __init__(self, device, parameters):
        super().__init__(device, parameters)
        self._restrict_parameters(must_disrupt=True, must_restore=False)
        self._vpn_server_ip = None

    def disrupt(self):
        L.describe('Block traffic to and from the VPN server with firewall rules')
        self._vpn_server_ip = self._device['vpn_application'].vpn_server_ip()
        self._device['firewall'].block_ip(self._vpn_server_ip)

    def teardown(self):
        if self._vpn_server_ip:
            self._device['firewall'].unblock_ip(self._vpn_server_ip)
        super().teardown()
