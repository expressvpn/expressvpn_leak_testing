import re

from xv_leak_tools.exception import XVEx
from xv_leak_tools.log import L
from xv_leak_tools.path import windows_path_split, windows_real_path
from xv_leak_tools.process import XVProcessException
from xv_leak_tools.test_device.desktop_device import DesktopDevice
from xv_leak_tools.test_device.connector_helper import ConnectorHelper

class WindowsDevice(DesktopDevice): # pylint: disable=no-self-use

    PROG_OS_VERSION = re.compile(r'OS Version:\s*([^\s]+).*')

    def __init__(self, config, connector):
        super().__init__(config, connector)
        self._connector_helper = ConnectorHelper(self)

    def _pgrep_cygwin(self, process_name):
        # -W shows windows processes under cygwin
        lines = self._connector_helper.check_command(['ps', '-efW'])[0].splitlines()
        lines = [line for line in lines if process_name in line]
        return [int(line.split()[1]) for line in lines]

    def is_cygwin(self):
        ret = self._connector_helper.execute_command(['uname'])[0]
        # Don't even need to check the output. This will fail if DOS.
        return ret == 0

    def os_name(self):
        return 'windows'

    def os_version(self):
        try:
            # Use systeminfo on Windows as platform.win32_ver doesn't work for cygwin. That way the
            # code is agnostic to the shell.
            output = self._connector_helper.check_command(['systeminfo'])[0]
            for line in output.splitlines():
                match = WindowsDevice.PROG_OS_VERSION.match(line)
                if match:
                    return match.group(1)
            raise XVEx(
                "Couldn't determine Windows Version from systeminfo output:\n{}".format(output))
        except XVProcessException as ex:
            raise XVEx("Couldn't determine Windows Version as systeminfo failed:\n{}".format(ex))

    # TODO: Not sure this will either work at all or work on cygwin
    def open_app(self, app_path, root=False): # pylint: disable=unused-argument
        # TODO: Oh dear god. This was painful!
        # Note that this can fail in a bad way. If start fails then it will pop a dialog box and
        # freeze everything. Need a better solution to this. Make sure paths are correct for now!
        head, tail = windows_path_split(app_path)
        cmd = ['cmd', '/C', 'start', '/D', "\"{}\"".format(windows_real_path(head)), tail]
        L.debug("Executing cmd '{}'".format(cmd))
        self._connector_helper.check_command(cmd)

    def close_app(self, app_path, root=False): # pylint: disable=unused-argument
        pname = windows_path_split(app_path)[1]
        pids = [str(pid) for pid in self.pgrep(pname)]
        if len(pids) > 1:
            L.warning(
                "Closing all pids {} associated to application {}".format(', '.join(pids), pname))
        for pid in pids:
            self.kill_process(pid)

    def kill_process(self, pid):
        L.debug("Killing process {}".format(pid))
        # taskkill is the most generic way to handle windows
        self._connector_helper.check_command(['taskkill', '/PID', str(pid), '/F'], root=True)

    def pgrep(self, process_name):
        '''Similar to the posix pgrep program, however it will return any process ids where
        process_name is a a substring of the whole process command line.'''
        L.debug("pgrep-ing for {}".format(process_name))
        if self.is_cygwin():
            return self._pgrep_cygwin(process_name)
        return self._connector_helper.execute_scriptlet('pgrep.py', [process_name], root=True)

    # This is pretty sketchy. Do better!
    @staticmethod
    def _fix_quotes(cmd_line):
        args = []
        next_arg = ""
        start_quote = False
        escaping = False
        for ichar, char in enumerate(cmd_line):
            if char not in ["\\", "\"", " "]:
                next_arg += char
                continue
            if char == "\"":
                if escaping:
                    next_arg += char
                    escaping = False
                    continue
                elif start_quote:
                    args.append(next_arg)
                    start_quote = False
                    next_arg = ""
                    continue
                else:
                    start_quote = True
                    continue
            elif char == "\\":
                if cmd_line[ichar + 1] == "\"":
                    escaping = True
                    next_arg += char
                else:
                    next_arg += char
                    continue
            elif char == " ":
                if start_quote:
                    next_arg += char
                    continue
                else:
                    if next_arg:
                        args.append(next_arg)
                        next_arg = ""
                    continue
        if next_arg != "":
            args.append(next_arg)
        return args

    def command_line_for_pid(self, pid):
        if self.is_cygwin():
            # The psutil module isn't supported on cygwin
            cmd = ["wmic", "process", "where", "ProcessID='{}'".format(pid), "get", "CommandLine"]
            args = self._connector_helper.check_command(cmd)[0]
            L.verbose("Raw wmic command line was: {}".format(args))
            return WindowsDevice._fix_quotes(args)

        return self._connector_helper.execute_scriptlet('command_line_for_pid.py', [pid])

    def report_info(self):
        info = super().report_info()
        try:
            info += self._connector_helper.check_command(['systeminfo'])[0]
        except XVProcessException as ex:
            L.warning("Couldn't get OS info from systeminfo:\n{}".format(ex))

        return info
