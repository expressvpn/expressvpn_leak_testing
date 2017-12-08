from xv_leak_tools.exception import XVEx
from xv_leak_tools.factory import Builder
from xv_leak_tools.test_components.cleanup.macos.macos_cleanup import MacOSCleanup
from xv_leak_tools.test_components.cleanup.android.android_cleanup import AndroidCleanup
from xv_leak_tools.test_components.cleanup.windows.windows_cleanup import WindowsCleanup
from xv_leak_tools.test_components.cleanup.ios.ios_cleanup import IOSCleanup
from xv_leak_tools.test_components.cleanup.linux.linux_cleanup import LinuxCleanup

class CleanupBuilder(Builder):

    @staticmethod
    def name():
        return 'cleanup'

    def build(self, device, config):
        if device.os_name() == 'macos':
            return MacOSCleanup(device, config)
        elif device.os_name() == 'windows':
            return WindowsCleanup(device, config)
        elif device.os_name() == 'linux':
            return LinuxCleanup(device, config)
        elif device.os_name() == 'android':
            return AndroidCleanup(device, config)
        elif device.os_name() == 'ios':
            return IOSCleanup(device, config)
        else:
            # Don't raise ComponentNotSupported as, if we get here, this implies something was
            # overlooked.
            raise XVEx("Don't know how to build 'cleanup' component for OS {}".format(
                device.os_name()))
