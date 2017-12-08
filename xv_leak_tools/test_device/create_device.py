from xv_leak_tools.exception import XVEx
from xv_leak_tools.test_device.android_device import AndroidDevice
from xv_leak_tools.test_device.ios_device import IOSDevice
from xv_leak_tools.test_device.linux_device import LinuxDevice
from xv_leak_tools.test_device.macos_device import MacOSDevice
from xv_leak_tools.test_device.router_device import RouterDevice
from xv_leak_tools.test_device.windows_device import WindowsDevice

# TODO: This is very rudimentary but until we need something more it's fine
def create_device(os_name, config, connector):
    if os_name == 'android':
        return AndroidDevice(config, connector)
    elif os_name == 'ios':
        return IOSDevice(config, connector)
    elif os_name == 'windows':
        return WindowsDevice(config, connector)
    elif os_name == 'linux':
        return LinuxDevice(config, connector)
    elif os_name == 'router':
        return RouterDevice(config, connector)
    elif os_name == 'macos':
        return MacOSDevice(config, connector)
    raise XVEx("Don't know how to create device for OS {}".format(os_name))
