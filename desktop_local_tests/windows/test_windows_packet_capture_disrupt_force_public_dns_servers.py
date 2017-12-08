from desktop_local_tests.local_packet_capture_test_case_with_disrupter import LocalPacketCaptureTestCaseWithDisrupter
from desktop_local_tests.windows.windows_dns_force_public_dns_servers_disrupter import WindowsDNSForcePublicDNSServersDisrupter

class TestWindowsPacketCaptureDisruptForcePublicDNSServers(LocalPacketCaptureTestCaseWithDisrupter):

    # TODO: Make the packet capture here DNS specific?

    def __init__(self, devices, parameters):
        super().__init__(WindowsDNSForcePublicDNSServersDisrupter, devices, parameters)
