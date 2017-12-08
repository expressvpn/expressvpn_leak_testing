from xv_leak_tools.log import L
from xv_leak_tools.test_components.cleanup.cleanup import Cleanup

class CleanupVPNs(Cleanup):

    # pylint: disable=too-many-arguments

    def __init__(
            self, device, config, vpn_process_names, vpn_applications, unkillable_applications):

        super().__init__(device, config)
        self._vpn_process_names = vpn_process_names
        self._vpn_applications = vpn_applications
        self._unkillable_applications = unkillable_applications

    def _vpn_processes(self):
        proceses = {}
        for pname in self._vpn_process_names:
            pids = self._device.pgrep(pname)
            if pids:
                proceses[pname] = self._device.pgrep(pname)
        return proceses

    def _force_kill_vpn_processes(self):
        for _, pid in list(self._vpn_processes().items()):
            self._device.kill_process(pid)

    def _disconnect_vpns(self):
        processes = self._vpn_processes()
        if not processes:
            return

        L.warning("The following VPN processes are running: {}".format(list(processes.keys())))

        # We have hanging VPN processes. Let's first try to disconnect the current one under test.
        self._device['vpn_application'].disconnect()

        # Try to force kill anything that's left
        # TODO: Don't think we should do this because many apps will auto-recover after this, thus
        # making it pointless.
        # self._force_kill_vpn_processes()

        processes = self._vpn_processes()
        if not processes:
            return

        L.warning(
            "The following VPN processes are still running: {}. Tests may not behave "
            "correctly!".format(list(processes.keys())))

    def _close_vpn_applications(self):
        for application in self._vpn_applications:
            for pid in self._device.pgrep(application):
                # Warn the user because ideally tests should start on a clean machine
                L.warning("Cleanup killing processes for application {}".format(application))
                self._device.kill_process(pid)

        for application in self._unkillable_applications:
            if self._device.pgrep(application):
                L.warning("Application {} is open but I don't know how to kill it".format(
                    application))

    def cleanup(self):
        self._disconnect_vpns()
        self._close_vpn_applications()
