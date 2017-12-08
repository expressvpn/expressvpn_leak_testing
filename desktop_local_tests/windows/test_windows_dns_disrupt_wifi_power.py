from desktop_local_tests.dns_during_disruption import DNSDuringDisruptionTestCase
from desktop_local_tests.windows.windows_wifi_power_disrupter import WindowsWifiPowerDisrupter

class TestWindowsDNSDisruptWifiPower(DNSDuringDisruptionTestCase):

    '''Summary:

    Test whether DNS leaks when the Wi-Fi power is disabled.

    Details:

    This test will connect to VPN then disable the Wi-Fi power. Once the power is disabled the
    test repeatedly makes DNS requests and checks whether the DNS request went to a non VPN DNS
    server

    Discussion:

    This test is somewhat of a stress test. A more realistic scenario with Wi-Fi is losing
    connectivity, e.g. by physically moving out of range of the Wi-Fi network's APs.

    Weaknesses:

    Currently uses dig to decide if DNS leaks. This isn't reliable for some VPN providers. Some
    providers intercept DNS upstream and change the destination DNS server to their own server.
    However dig will still report the server which it originally sent the request to.

    Scenarios:

    * Run test when Wi-Fi is the primary adapter
    * Run test when Wi-Fi is NOT the primary adapter
    '''

    def __init__(self, devices, parameters):
        super().__init__(WindowsWifiPowerDisrupter, devices, parameters)
