from xv_leak_tools.log import L
from xv_leak_tools.test_device.mobile_device import MobileDevice
from xv_leak_tools.test_device.shell_connector_helper import ShellConnectorHelper

class AndroidDevice(MobileDevice):

    def __init__(self, config, connector):
        super().__init__(config, connector)
        self._connector_helper = ShellConnectorHelper(self)

    @staticmethod
    def os_name():
        return 'android'

    def os_version(self):
        L.warning("Android version detection not implemented")
        return 'TODO: Android version'

    def open_app(self, bundle, activity, root=False):
        cmd = "am start -n {}/.{}".format(bundle, activity)
        self._connector_helper.check_command(cmd.split(), root)

    def close_app(self, bundle, root=False):
        cmd = "am force-stop {}".format(bundle)
        self._connector_helper.check_command(cmd.split(), root)

    def run_cmd(self, cmd, root=False):
        return self._connector_helper.check_command(cmd, root)

    def wakeup(self):
        L.debug("Waking device up")
        cmd = "input keyevent WAKEUP && input keyevent MENU"
        self._connector_helper.check_command(cmd.split())

    def sleep(self):
        L.debug("Go back to sleep")
        cmd = "input keyevent SOFT_SLEEP"
        self._connector_helper.check_command(cmd.split())

    def close_tray(self):
        cmd = "input swipe 10 900 10 10 100 && input swipe 10 900 10 10 100"
        self._connector_helper.check_command(cmd.split())

    def kill_process(self, pid):
        L.debug("Killing process {}".format(pid))
        L.warning("Not implemented!")

    def pgrep(self, process_name):
        L.debug("pgrep-ing for {}".format(process_name))
        L.warning("Not implemented!")

    def focused_activity(self):
        cmd = "dumpsys activity activities | grep mFocusedActivity | cut -d ' ' -f 6"
        return self._connector_helper.check_command(cmd.split())[1].strip()
