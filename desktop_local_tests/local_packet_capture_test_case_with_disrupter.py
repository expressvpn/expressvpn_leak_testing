from desktop_local_tests.local_packet_capture_test_case import LocalPacketCaptureTestCase
from xv_leak_tools.log import L

class LocalPacketCaptureTestCaseWithDisrupter(LocalPacketCaptureTestCase):

    def __init__(self, disrupter_class, devices, parameters):
        super().__init__(devices, parameters)
        self.disrupter = disrupter_class(self.localhost, self.parameters)

    def setup(self):
        super().setup()
        self.disrupter.setup()

    def test_with_packet_capture(self):
        L.describe("Create disruption...")
        self.disrupter.create_disruption()

    def teardown(self):
        self.disrupter.teardown()
        super().teardown()
