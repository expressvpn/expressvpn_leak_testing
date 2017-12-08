from desktop_local_tests.disrupter import Disrupter
from xv_leak_tools.log import L

class DisrupterKillVPNProcess(Disrupter):

    def __init__(self, device, parameters):
        super().__init__(device, parameters)
        self._restrict_parameters(must_disrupt=True, must_restore=False)

    def disrupt(self):
        L.describe('Find the VPN processes and kill them (not the main application)')
        pids = self._device['vpn_application'].vpn_processes()
        self.assertNotEmpty(pids, 'Found no VPN processes. This should not happen')

        for pid in pids:
            self._device.kill_process(pid)
            L.info("Killed VPN process (PID {})".format(pid))
