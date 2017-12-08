from desktop_local_tests.dns_during_disruption import DNSDuringDisruptionTestCase
from desktop_local_tests.disrupter_kill_vpn_process import DisrupterKillVPNProcess

class TestDNSDisruptKillVPNProcess(DNSDuringDisruptionTestCase):

    '''Summary:

    Test whether DNS leaks when the VPN process crashes.

    Details:

    This test will kill the underlying process responsible for providing the VPN service. For
    example, it will kill the openvpn binary when using OpenVPN. It does not kill any other support
    processes for the provider, e.g. UI app, daemons etc..

    Discussion:

    The test is a stress test. Crashes should be rare but in the real world they can happen. A VPN
    should be resilient to such crashes.

    Weaknesses:

    Currently uses dig to decide if DNS leaks. This isn't reliable for some VPN providers. Some
    providers intercept DNS upstream and change the destination DNS server to their own server.
    However dig will still report the server which it originally sent the request to.

    Scenarios:

    No restrictions.

    TODO:

    Consider tests which kill other/all processes related to a VPN.
    '''

    def __init__(self, devices, parameters):
        super().__init__(DisrupterKillVPNProcess, devices, parameters)
