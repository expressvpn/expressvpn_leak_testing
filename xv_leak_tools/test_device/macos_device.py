import ipaddress
import signal
import netifaces

from xv_leak_tools.log import L
from xv_leak_tools.test_device.desktop_device import DesktopDevice
from xv_leak_tools.test_device.connector_helper import ConnectorHelper
from xv_leak_tools.process import XVProcessException

class MacOSDevice(DesktopDevice):

    def __init__(self, config, connector):
        super().__init__(config, connector)
        # TODO: I think this should be part of DesktopDevice. Need to clarify what all these thigns
        # mean. I think we should move to DesktopDevice meaning anything with the tools. Maybe even
        # this becomes ToolsDevice.
        self._connector_helper = ConnectorHelper(self)

    # TODO: This needs to execute remotely in general. Let's make a scriptlet. Let's ensure that
    # nothing on the device classes themselves restricts the devices to being the localhost
    @staticmethod
    def local_ips():
        ips = []
        for iface in netifaces.interfaces():
            if netifaces.AF_INET in netifaces.ifaddresses(iface):
                ips.append(netifaces.ifaddresses(iface)[netifaces.AF_INET][0]['addr'])
        return [ipaddress.ip_address(ip) for ip in ips]

    def open_app(self, bundle_path, root=False):
        # Quote the bundle path as some have spaces in
        self._connector_helper.execute_scriptlet(
            'macos_open_app.py', ["'{}'".format(bundle_path)], root=root)

    def close_app(self, bundle_path, root=False):
        # Quit by sending quit signal to the window so the app shuts down how a user would shut it
        # down. In theory it's equivalent to a pkill but slightly more realistic this way
        self._connector_helper.execute_command(
            ['osascript', '-e', "'quit app \"{}\"'".format(bundle_path)], root=root)

    def os_name(self):
        return 'macos'

    def os_version(self):
        return self._connector_helper.execute_scriptlet('remote_mac_ver.py', [])[0]

    def report_info(self):
        info = super().report_info()
        try:
            info += self._connector_helper.check_command(
                ['system_profiler', 'SPSoftwareDataType'])[0]
        except XVProcessException as ex:
            L.warning("Couldn't get OS info from system_profiler:\n{}".format(ex))

        return info

    def kill_process(self, pid):
        L.debug("Killing process {}".format(pid))
        return self._connector_helper.execute_scriptlet(
            'remote_os_kill.py', [pid, int(signal.SIGKILL)], root=True)

    def pgrep(self, process_name):
        '''Similar to the posix pgrep program, however it will return any process ids where
        process_name is a a substring of the whole process command line.'''
        L.debug("pgrep-ing for {}".format(process_name))
        return self._connector_helper.execute_scriptlet('pgrep.py', [process_name], root=True)

    def command_line_for_pid(self, pid):
        return self._connector_helper.execute_scriptlet('command_line_for_pid.py', [pid], root=True)
