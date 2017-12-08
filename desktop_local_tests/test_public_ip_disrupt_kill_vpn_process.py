from desktop_local_tests.public_ip_during_disruption import PublicIPDuringDisruptionTestCase
from desktop_local_tests.disrupter_kill_vpn_process import DisrupterKillVPNProcess

class TestPublicIPDisruptKillVPNProcess(PublicIPDuringDisruptionTestCase):

    '''Summary:

    Test whether the device's public IP is exposed when the VPN process crashes.

    Details:

    This test will kill the underlying process responsible for providing the VPN service. For
    example, it will kill the openvpn binary when using OpenVPN. It does not kill any other support
    processes for the provider, e.g. UI app, daemons etc.. Once the process has been killed, the
    repeatedly checks the device's public IPv4 and IPv6 addresses by visiting a webpage designed to
    report those IPs.

    Discussion:

    The test is a stress test. Crashes should be rare but in the real world they can happen. A VPN
    should be resilient to such crashes.

    Weaknesses:

    The time taken to perform each IP request is relatively long. Tests using IPResponder should be
    preferred over these tests.

    Scenarios:

    No restrictions.
    '''

    def __init__(self, devices, parameters):
        super().__init__(DisrupterKillVPNProcess, devices, parameters)
