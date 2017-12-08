from desktop_local_tests.local_ip_responder_test_case_with_disrupter import LocalIPResponderTestCaseWithDisrupter
from desktop_local_tests.windows.windows_wifi_power_disrupter import WindowsWifiPowerDisrupter

class TestWindowsIPResponderDisruptWifiPower(LocalIPResponderTestCaseWithDisrupter):

    '''Summary:

    Tests whether traffic leaving the user's device has the public IP hidden when the Wi-Fi power is
    disabled.

    Details:

    This test will connect to VPN then disable the Wi-Fi power.

    This test uses a simple UDP client which spams UDP packets to a public server. The server logs
    the source IP of every packet. The test checks with the server to make sure that the public IP
    is always the VPN server's IP and not the device's.

    Discussion:

    This test is somewhat of a stress test. A more realistic scenario with Wi-Fi is losing
    connectivity, e.g. by physically moving out of range of the Wi-Fi network's APs.

    Weaknesses:

    None

    Scenarios:

    * Run test when Wi-Fi is the primary adapter
    * Run test when Wi-Fi is NOT the primary adapter
    '''

    def __init__(self, devices, parameters):
        super().__init__(WindowsWifiPowerDisrupter, devices, parameters)
