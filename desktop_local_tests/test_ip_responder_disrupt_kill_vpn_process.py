from desktop_local_tests.local_ip_responder_test_case_with_disrupter import LocalIPResponderTestCaseWithDisrupter
from desktop_local_tests.disrupter_kill_vpn_process import DisrupterKillVPNProcess

class TestIPResponderDisruptKillVPNProcess(LocalIPResponderTestCaseWithDisrupter):

    '''Summary:

    Tests whether traffic leaving the user's device has the public IP hidden when the VPN process
    crashes.

    Details:

    This test will kill the underlying process responsible for providing the VPN service. For
    example, it will kill the openvpn binary when using OpenVPN. It does not kill any other support
    processes for the provider, e.g. UI app, daemons etc..

    This test uses a simple UDP client which spams UDP packets to a public server. The server logs
    the source IP of every packet. The test checks with the server to make sure that the public IP
    is always the VPN server's IP and not the device's.

    Discussion:

    The test is a stress test. Crashes should be rare but in the real world they can happen. A VPN
    should be resilient to such crashes.

    Weaknesses:

    None

    Scenarios:

    No restrictions.

    TODO:

    Consider tests which kill other/all processes related to a VPN.

    '''

    def __init__(self, devices, parameters):
        super().__init__(DisrupterKillVPNProcess, devices, parameters)
