from desktop_local_tests.local_packet_capture_test_case_with_disrupter import LocalPacketCaptureTestCaseWithDisrupter
from desktop_local_tests.windows.windows_wifi_power_disrupter import WindowsWifiPowerDisrupter

class TestWindowsPacketCaptureDisruptWifiPower(LocalPacketCaptureTestCaseWithDisrupter):

    '''Summary:

    Tests whether traffic leaving the user's device leaks outside of the VPN tunnel when the Wi-Fi
    power is disabled.

    Details:

    This test will connect to VPN then disable the Wi-Fi power. The test looks for leaking traffic
    once the interface has been disabled.

    Discussion:

    This test is somewhat of a stress test. A more realistic scenario with Wi-Fi is losing
    connectivity, e.g. by physically moving out of range of the Wi-Fi network's APs.

    Weaknesses:

    Packet capture tests can be noisy. Traffic can be detected as a leak but in actual fact may not
    be. For example, traffic might go to a server owned by the VPN provider to re-establish
    connections. In general this test is best used for manual exploring leaks rather than for
    automation.

    Scenarios:

    * Run test when Wi-Fi is the primary adapter
    * Run test when Wi-Fi is NOT the primary adapter
    '''

    def __init__(self, devices, parameters):
        super().__init__(WindowsWifiPowerDisrupter, devices, parameters)
