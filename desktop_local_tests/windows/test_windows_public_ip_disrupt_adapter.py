from desktop_local_tests.public_ip_during_disruption import PublicIPDuringDisruptionTestCase
from desktop_local_tests.windows.windows_adapter_disrupter import WindowsAdapterDisrupter

class TestWindowsPublicIPDisruptAdapter(PublicIPDuringDisruptionTestCase):

    '''Summary:

    Tests whether traffic leaving the user's device has the public IP hidden when the network
    adapter is disabled.

    Details:

    This test will connect to VPN then disable the primary adapter, which will be the one
    used to connect to the VPN. The test then queries a webpage to detect it's public IP.

    Discussion:

    It is unlikely that the adapter would be disabled in this way in the real world, but of course
    not impossible. However, this represents a class of tests which disrupt the primary network
    adapter. Other types of disruption would be:

    * Ethernet cable pulled (see TestDNSDisruptCable)
    * Wi-Fi power disabled (see TestWindowsOSDNSDisruptWifiPower)
    * Wi-Fi network unavailable, e.g. walk out of range of Wi-Fi network.

    Weaknesses:

    The time taken to perform each IP request is relatively long. Tests using IPResponder should be
    preferred over these tests.

    Scenarios:

    No restrictions.

    TODO:

    This class only disables the primary adapter. Would be good to try permutations like:

        * Disable all adapters
          * This opens up a class of behaviour tests of "what does my VPN do when I lose all
            connectivity but then get it back later"
        * Disable a secondary adapter
        * Disable all but the primary adapter
        * Implement Wi-Fi unavailable tests

    This behaviour should be configurable from the test config.
    '''

    def __init__(self, devices, parameters):
        super().__init__(WindowsAdapterDisrupter, devices, parameters)
