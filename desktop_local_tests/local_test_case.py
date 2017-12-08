from xv_leak_tools.exception import XVEx
from xv_leak_tools.helpers import TimeUp
from xv_leak_tools.log import L
from xv_leak_tools.test_framework.test_case import TestCase

class LocalTestCase(TestCase):

    def __init__(self, devices, parameters):
        super().__init__(devices, parameters)
        self.localhost = self.devices['localhost']

    def _check_network(self):
        L.info("Checking if there's a network connection")
        timeup = TimeUp(5)
        while not timeup:
            lost = self.localhost['network_tool'].ping('8.8.8.8', count=3, timeout=2)
            if lost == 3:
                L.warning(
                    "No network detected. Will try for {} seconds.".format(timeup.time_left()))
            elif lost == 0:
                L.info("Network okay")
                return
            else:
                L.warning("Network detected but there's some packet loss")
                return
        raise XVEx(
            "No network connection detected. Tests must be started with an active network. "
            "Do you have any VPN applications open?")

    def setup(self):
        super().setup()

        # TODO: Not sure all this stuff belongs here. Probably belongs in a derived class
        L.describe("Ensure no VPN apps are connected or open")
        self.localhost['cleanup'].cleanup()

        self._check_network()

        L.describe("Configure VPN application")
        self.localhost['vpn_application'].configure()

    def teardown(self):
        self.localhost['vpn_application'].disconnect()
        self.localhost['vpn_application'].close()

        super().teardown()
