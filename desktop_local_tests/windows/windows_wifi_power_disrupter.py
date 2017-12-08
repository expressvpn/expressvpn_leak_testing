from desktop_local_tests.disrupter import Disrupter
from xv_leak_tools.log import L
from xv_leak_tools.manual_input import message_and_await_enter

class WindowsWifiPowerDisrupter(Disrupter):

    VIA = 'via the Start->Settings->Network & Internet->Wi-Fi'

    def disrupt(self):
        L.describe('Disable Wi-Fi')
        # TODO: I have no idea how to do this programmatically yet (or if it's even possible).
        # Probably it can be done via a registry setting
        message_and_await_enter("Disable Wi-Fi {}".format(WindowsWifiPowerDisrupter.VIA))

    def restore(self):
        L.describe('Re-enable Wi-Fi')
        message_and_await_enter("Re-enable Wi-Fi {}".format(WindowsWifiPowerDisrupter.VIA))

    def teardown(self):
        self.restore()
        super().teardown()
