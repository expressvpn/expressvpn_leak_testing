import platform
import signal

from xv_leak_tools.exception import XVEx
from xv_leak_tools.helpers import unused
from xv_leak_tools.log import L
from xv_leak_tools.test_device.desktop_device import DesktopDevice
from xv_leak_tools.test_device.connector_helper import ConnectorHelper
from xv_leak_tools.process import XVProcessException

# TODO: consider a UnixDevice as ancestor of MacOSDevice, LinuxDevice

class LinuxDevice(DesktopDevice):

    def __init__(self, config, connector):
        super().__init__(config, connector)
        self._connector_helper = ConnectorHelper(self)

    @staticmethod
    def local_ips():
        raise XVEx("TODO: Local IPs for Linux")

    @staticmethod
    def open_app(binary_path, root=False):
        unused(root)
        if binary_path is None:
            L.debug('Application has no binary path; not opening')
        # TODO: open the application here

    @staticmethod
    def close_app(binary_path, root=False):
        unused(root)
        if binary_path is None:
            L.debug('Application has no binary path; not closing')
        # TODO: close the application here

    def os_name(self):
        return 'linux'

    def os_version(self):
        return " ".join(platform.linux_distribution())

    def report_info(self):
        info = super().report_info()
        commands = [
            ['uname', '-a'],
            ['lsb_release', '-a'],
            ['lscpu'],
        ]
        for command in commands:
            try:
                info += self._connector_helper.check_command(command)[0]
            except XVProcessException as ex:
                L.warning("Couldn't get system info using command {}:\n{}".format(command, ex))

        return info

    def kill_process(self, pid):
        L.debug("Killing process {}".format(pid))
        return self._connector_helper.execute_scriptlet(
            'remote_os_kill.py', [pid, int(signal.SIGKILL)], root=True)

    def pgrep(self, process_name):
        L.debug("pgrep-ing for {}".format(process_name))
        return self._connector_helper.execute_scriptlet('pgrep.py', [process_name], root=True)

    def command_line_for_pid(self, pid):
        return self._connector_helper.execute_scriptlet('command_line_for_pid.py', [pid], root=True)
