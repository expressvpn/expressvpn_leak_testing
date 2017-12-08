from xv_leak_tools.factory import Builder
from xv_leak_tools.test_components.component import ComponentNotSupported
from xv_leak_tools.test_components.settings.android_settings import AndroidSettings
from xv_leak_tools.test_components.settings.ios_settings import IOSSettings

class SettingsBuilder(Builder):

    @staticmethod
    def name():
        return 'settings'

    def build(self, device, config):
        if device.os_name() == 'android':
            return AndroidSettings(device, config)
        elif device.os_name() == 'ios':
            return IOSSettings(device, config)
        raise ComponentNotSupported("settings is not currently supported on {}".format(
            device.os_name()))
