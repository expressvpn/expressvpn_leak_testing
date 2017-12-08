from desktop_local_tests.public_ip_during_disruption import PublicIPDuringDisruptionTestCase
from desktop_local_tests.vpn_connection_disrupter import VPNConnectionDisrupter

class TestPublicIPDisruptVPNConnection(PublicIPDuringDisruptionTestCase):

    '''Summary:

    Tests whether traffic leaving the user's device has the public IP hidden when the VPN server
    becomes unreachable.

    Details:

    This test will connect to VPN then put up firewall rules which block connectivity to the VPN
    server. The test then queries a webpage to detect it's public IP.

    Discussion:

    Connectivity drops to the VPN server are very real world threats. This could happen for a
    variety of reasons:

    * Server goes down
    * Server is deliberately taken out of rotation for maintenance etc..
    * Blocking
    * Bad routes

    In all cases a firewall adequately represents these connectivity drops.

    Weaknesses:

    The time taken to perform each IP request is relatively long. Tests using IPResponder should be
    preferred over these tests.

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
