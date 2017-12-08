import time
from xv_leak_tools.log import L
from xv_leak_tools.test_components.settings.settings import Settings

class AndroidSettings(Settings):

    def enable_wifi(self):
        L.info('Enabling WiFi')
        cmd = ["svc", "wifi", "enable"]
        self._device.connector().execute(cmd, root=True)
        L.debug('Sleeping for 5 seconds')
        time.sleep(5)

    def disable_wifi(self):
        L.info('Disabling WiFi')
        cmd = ["svc", "wifi", "disable"]
        self._device.connector().execute(cmd, root=True)

    def enable_mobile_data(self):
        L.info('Enabling mobile data')
        cmd = ["svc", "data", "enable"]
        return self._device.connector().execute(cmd, root=True)

    def disable_mobile_data(self):
        L.info('Disabling mobile data')
        cmd = ["svc", "data", "disable"]
        self._device.connector().execute(cmd, root=True)

    def enable_airplane_mode(self):
        L.info('Enabling airplane mode')
        cmd = ['settings', 'put', 'global', 'airplane_mode_on', '1']
        self._device.connector().execute(cmd, root=False)
        cmd = ['am', 'broadcast', '-a', 'android.intent.action.AIRPLANE_MODE']
        self._device.connector().execute(cmd, root=True)

    def disable_airplane_mode(self):
        L.info('Disabling airplane mode')
        cmd = ['settings', 'put', 'global', 'airplane_mode_on', '0']
        self._device.connector().execute(cmd, root=False)
        cmd = ['am', 'broadcast', '-a', 'android.intent.action.AIRPLANE_MODE']
        self._device.connector().execute(cmd, root=True)
