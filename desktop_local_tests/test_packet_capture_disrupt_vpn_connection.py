from desktop_local_tests.local_packet_capture_test_case_with_disrupter import LocalPacketCaptureTestCaseWithDisrupter
from desktop_local_tests.vpn_connection_disrupter import VPNConnectionDisrupter

class TestPacketCaptureDisruptVPNConnection(LocalPacketCaptureTestCaseWithDisrupter):

    '''Summary:

    Tests whether traffic leaving the user's device leaks outside of the VPN tunnel when the VPN
    server becomes unreachable.

    Details:

    This test will connect to VPN then put up firewall rules which block connectivity to the VPN
    server. The test looks for leaking traffic once the interface has been disabled.

    Discussion:

    Connectivity drops to the VPN server are very real world threats. This could happen for a
    variety of reasons:

    * Server goes down
    * Server is deliberately taken out of rotation for maintenance etc..
    * Blocking
    * Bad routes

    In all cases a firewall adequately represents these connectivity drops.

    Weaknesses:

    Packet capture tests can be noisy. Traffic can be detected as a leak but in actual fact may not
    be. For example, traffic might go to a server owned by the VPN provider to re-establish
    connections. In general this test is best used for manual exploring leaks rather than for
    automation.

    With some systems/VPN applications, a firewall on the test device might not adequately block the
    VPN server. For such setups, a secondary device is needed e.g.

    * Firewall on a router
    * Firewall on host if the test device is a VM.

    Scenarios:

    No restrictions.

    TODO:

    Implement multi-device test with firewall off device

    '''


    def __init__(self, devices, parameters):
        super().__init__(VPNConnectionDisrupter, devices, parameters)
