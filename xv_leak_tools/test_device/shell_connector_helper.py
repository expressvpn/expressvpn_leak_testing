from xv_leak_tools.process import XVProcessException

class ShellConnectorHelper:

    # pylint: disable=too-few-public-methods

    def __init__(self, device):
        self._device = device

    def check_command(self, cmd, root=False):
        ret, stdout, stderr = self._device.connector().execute(cmd, root)
        if ret:
            raise XVProcessException(cmd, ret, stdout, stderr)
        return ret, stdout, stderr
