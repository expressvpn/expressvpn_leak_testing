from desktop_local_tests.public_ip_during_disruption import PublicIPDuringDisruptionTestCase
from desktop_local_tests.windows.windows_wifi_power_disrupter import WindowsWifiPowerDisrupter

class TestWindowsPublicIPDisruptWifiPower(PublicIPDuringDisruptionTestCase):

    '''Summary:

    Tests whether traffic leaving the user's device has the public IP hidden when the Wi-Fi power is
    disabled.

    Details:

    This test will connect to VPN then disable the Wi-Fi power. The test then queries a webpage to
    detect it's public IP.

    Discussion:

    This test is somewhat of a stress test. A more realistic scenario with Wi-Fi is losing
    connectivity, e.g. by physically moving out of range of the Wi-Fi network's APs.

    Weaknesses:

    The time taken to perform each IP request is relatively long. Tests using IPResponder should be
    preferred over these tests.

    Scenarios:

    * Run test when Wi-Fi is the primary adapter
    * Run test when Wi-Fi is NOT the primary adapter
    '''

    def __init__(self, devices, parameters):
        super().__init__(WindowsWifiPowerDisrupter, devices, parameters)
