# from xv_leak_tools.exception import XVEx
# from xv_leak_tools.log import L
from xv_leak_tools.process import execute_subprocess
from xv_leak_tools.test_device.local_shell_connector import LocalShellConnector

class WindowsLocalShellConnector(LocalShellConnector):

    def execute(self, cmd, root=False):
        # TODO: Don't have the ability to change to/from root on Windows. Any clean way of doing
        # this?
        return execute_subprocess(cmd)

    # def push(self, src, dst):
    #     ret, stdout, stderr = execute_subprocess(['cp', '-rf', src, dst])

    #     if ret != 0:
    #         raise XVEx("Couldn't copy {} -> {}: stdout: {}, stderr: {}".format(
    #             src, dst, stdout, stderr))

    #     if os.geteuid() != 0:
    #         return

    #     # When executing locally it's entirely likely we'll be running as root. We don't want to
    #     # have any files owned by root unless directly specified by the user - in which case they
    #     # should chown via a command for now (which I think is an unlikely use case).

    #     L.verbose("Removing root permissions from file {} ({})".format(dst, tools_user()[0]))
    #     os.chown(dst, tools_user()[0], -1)

    # def pull(self, src, dst):
    #     self.push(src, dst)
