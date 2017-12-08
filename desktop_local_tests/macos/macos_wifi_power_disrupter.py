from desktop_local_tests.disrupter import Disrupter
from xv_leak_tools.log import L

class MacOSWifiPowerDisrupter(Disrupter):

    def __init__(self, device, parameters):
        super().__init__(device, parameters)
        self.wifi_service = self._find_wifi_service()

    def _find_wifi_service(self):
        wifi_service = self._device['network_tool'].wifi_service()
        L.info("WiFi network service is {}".format(wifi_service.name()))
        return wifi_service

    def disrupt(self):
        L.describe('Disable power on the Wi-Fi network service')
        self.wifi_service.disable_wifi_power()

    def restore(self):
        L.describe('Re-enable power on the Wi-Fi network service')
        self.wifi_service.enable_wifi_power()

    def teardown(self):
        if self.wifi_service:
            self.wifi_service.enable_wifi_power()
        super().teardown()
