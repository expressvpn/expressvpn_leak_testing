from desktop_local_tests.local_packet_capture_test_case_with_disrupter_and_generator import LocalPacketCaptureTestCaseWithDisrupterAndGenerator
from desktop_local_tests.vpn_connection_disrupter import VPNConnectionDisrupter

class TestPacketCaptureDisruptVPNConnectionAndGenerateTraffic(
        LocalPacketCaptureTestCaseWithDisrupterAndGenerator):

    # TODO: Docs

    def __init__(self, devices, parameters):
        super().__init__(VPNConnectionDisrupter, devices, parameters)
