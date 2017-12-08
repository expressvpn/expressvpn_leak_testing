from desktop_local_tests.dns_during_disruption import DNSDuringDisruptionTestCase
from desktop_local_tests.vpn_connection_disrupter import VPNConnectionDisrupter

class TestDNSDisruptVPNConnection(DNSDuringDisruptionTestCase):

    '''Summary:

    Test whether DNS leaks when the VPN server becomes unreachable.

    Details:

    This test will connect to VPN then put up firewall rules which block connectivity to the VPN
    server. Once the rules are up the test repeatedly makes DNS requests and checks whether the DNS
    request went to a non VPN DNS server a DNS leak.

    Discussion:

    Connectivity drops to the VPN server are very real world threats. This could happen for a
    variety of reasons:

    * Server goes down
    * Server is deliberately taken out of rotation for maintenance etc..
    * Blocking
    * Bad routes

    In all cases a firewall adequately represents these connectivity drops.

    Weaknesses:

    Currently uses dig to decide if DNS leaks. This isn't reliable for some VPN providers. Some
    providers intercept DNS upstream and change the destination DNS server to their own server.
    However dig will still report the server which it originally sent the request to.

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
