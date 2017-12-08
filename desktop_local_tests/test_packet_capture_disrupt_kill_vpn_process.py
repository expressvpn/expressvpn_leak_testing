from desktop_local_tests.local_packet_capture_test_case_with_disrupter import LocalPacketCaptureTestCaseWithDisrupter
from desktop_local_tests.disrupter_kill_vpn_process import DisrupterKillVPNProcess

class TestPacketCaptureDisruptKillVPNProcess(LocalPacketCaptureTestCaseWithDisrupter):

    '''Summary:

    Test whether traffic leaks when the VPN process crashes.

    Details:

    This test will kill the underlying process responsible for providing the VPN service. For
    example, it will kill the openvpn binary when using OpenVPN. It does not kill any other support
    processes for the provider, e.g. UI app, daemons etc..

    Discussion:

    The test is a stress test. Crashes should be rare but in the real world they can happen. A VPN
    should be resilient to such crashes.

    Weaknesses:

    Packet capture tests can be noisy. Traffic can be detected as a leak but in actual fact may not
    be. For example, traffic might go to a server owned by the VPN provider to re-establish
    connections. In general this test is best used for manual exploring leaks rather than for
    automation.

    Scenarios:

    No restrictions.

    TODO:

    Consider tests which kill other/all processes related to a VPN.
    '''

    def __init__(self, devices, parameters):
        super().__init__(DisrupterKillVPNProcess, devices, parameters)
