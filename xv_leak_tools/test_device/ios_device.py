from xv_leak_tools.log import L
from xv_leak_tools.test_device.mobile_device import MobileDevice
from xv_leak_tools.test_device.shell_connector_helper import ShellConnectorHelper

class IOSDevice(MobileDevice):

    def __init__(self, config, connector):
        super().__init__(config, connector)
        self._connector_helper = ShellConnectorHelper(self)

    @staticmethod
    def os_name():
        return 'ios'

    def os_version(self):
        L.warning("iOS version detection not implemented")
        return 'TODO: iOS version'

    def open_app(self, bundle, activity, root=False):
        pass

    def close_app(self, bundle, root=False):
        pass

    def run_cmd(self, cmd, root=False):
        return self._connector_helper.check_command(cmd, root)

    def wakeup(self):
        L.debug("Waking device up")

    def sleep(self):
        L.debug("Go back to sleep")

    def close_tray(self):
        pass

    def kill_process(self, pid):
        L.debug("Killing process {}".format(pid))
        L.warning("Not implemented!")

    def pgrep(self, process_name):
        L.debug("pgrep-ing for {}".format(process_name))
        L.warning("Not implemented!")

    def focused_activity(self):
        pass
