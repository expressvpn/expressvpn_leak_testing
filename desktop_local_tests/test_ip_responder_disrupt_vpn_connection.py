from desktop_local_tests.local_ip_responder_test_case_with_disrupter import LocalIPResponderTestCaseWithDisrupter
from desktop_local_tests.vpn_connection_disrupter import VPNConnectionDisrupter

# TODO: Replace the mac specific tests which use VPNConnectionDisrupter. VPNConnectionDisrupter
# is generic
class TestIPResponderDisruptVPNConnection(LocalIPResponderTestCaseWithDisrupter):

    '''Summary:

    Tests whether traffic leaving the user's device has the public IP hidden when the VPN server
    becomes unreachable.

    Details:

    This test will connect to VPN then put up firewall rules which block connectivity to the VPN
    server.

    This test uses a simple UDP client which spams UDP packets to a public server. The server logs
    the source IP of every packet. The test checks with the server to make sure that the public IP
    is always the VPN server's IP and not the device's.

    Discussion:

    Connectivity drops to the VPN server are very real world threats. This could happen for a
    variety of reasons:

    * Server goes down
    * Server is deliberately taken out of rotation for maintenance etc..
    * Blocking
    * Bad routes

    In all cases a firewall adequately represents these connectivity drops.

    Weaknesses:

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
