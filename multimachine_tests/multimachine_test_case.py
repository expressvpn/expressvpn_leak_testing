from xv_leak_tools.log import L
from xv_leak_tools.test_framework.test_case import TestCase
from xv_leak_tools.traffic_filter import TrafficFilter
from xv_leak_tools.traffic_analyser import TrafficAnalyser

class MultimachineTestCase(TestCase):

    def __init__(self, devices, config):
        super().__init__(devices, config)
        self.target_device = self.devices['target_device']
        self.capture_device = self.devices['packet_capture_device']
        self.traffic_analyser = TrafficAnalyser()
        self.traffic_filter = TrafficFilter

    def setup(self):
        super().setup()

        L.describe('Ensure no VPN apps are connected or open')
        self.target_device['cleanup'].cleanup()

        L.describe('Configure VPN application')
        self.target_device['vpn_application'].configure()

    def teardown(self):
        self.target_device['vpn_application'].disconnect()
        self.target_device['vpn_application'].close()
        super().teardown()
