from collections import namedtuple
from xv_leak_tools.process import execute_subprocess, XVProcessException
from xv_leak_tools.exception import XVEx
from xv_leak_tools.log import L
from xv_leak_tools.test_device.connector import Connector

class ADBConnector(Connector):

    def __init__(self, adb_id):
        self.adb_id = adb_id

    @staticmethod
    def _start_adb_server():
        ret, _, stderr = execute_subprocess(['adb', 'start-server'])
        if ret:
            raise XVEx('Could not start the ADB server: {}.'.format(stderr))

    @staticmethod
    def _adb_devices():
        device_list = execute_subprocess(['adb', 'devices', '-l'])[1].split()[4:]
        device_list = [device_list[i:i + 6] for i in range(0, len(device_list), 6)]
        adb_device = namedtuple('adb_device',
                                ['adb_id', 'usb', 'product', 'model', 'device'])
        for device in device_list:
            yield adb_device(adb_id=device[0],
                             usb=device[2].split(':')[1],
                             product=device[3].split(':')[1],
                             model=device[4].split(':')[1],
                             device=device[5].split(':')[1],
                            )

    def _device_exists(self):
        for device in ADBConnector._adb_devices():
            if self.adb_id == device.adb_id:
                return True
        return False

    def _ensure_connected(self):
        ADBConnector._start_adb_server()
        if not self._device_exists():
            raise XVEx('ADB device {} does not exist.'.format(self.adb_id))

    def _run_adb_cmd(self, cmd):
        self._ensure_connected()
        cmd = ['adb', '-s', self.adb_id] + cmd
        return execute_subprocess(cmd)

    def _check_adb_cmd(self, cmd):
        ret, stdout, stderr = self._run_adb_cmd(cmd)
        if ret:
            raise XVProcessException(cmd, ret, stdout, stderr)
        return ret, stdout, stderr

    def execute(self, cmd, root=False):
        if root:
            # TODO: This doesn't include the "adb root shell" way of doing
            # things, because it depends on the root method. It would be
            # nice/necessary to support both.
            L.debug('ADB (root): {}'.format(' '.join(cmd)))
            return self._run_adb_cmd(['shell', 'su', '-c'] + cmd)
        L.debug('ADB: {}'.format(' '.join(cmd)))
        return self._run_adb_cmd(['shell'] + cmd)

    def push(self, src, dst):
        return self._check_adb_cmd(['push', src, dst])

    def pull(self, src, dst):
        return self._check_adb_cmd(['pull', src, dst])
