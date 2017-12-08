from desktop_local_tests.local_ip_responder_test_case_with_disrupter import LocalIPResponderTestCaseWithDisrupter
from desktop_local_tests.windows.windows_adapter_disrupter import WindowsAdapterDisrupter

class TestWindowsIPResponderDisruptAdapter(LocalIPResponderTestCaseWithDisrupter):

    '''Summary:

    Tests whether traffic leaving the user's device has the public IP hidden when the network
    adapter is disabled.

    Details:

    This test will connect to VPN then disable the primary network adapter.

    This test uses a simple UDP client which spams UDP packets to a public server. The server logs
    the source IP of every packet. The test checks with the server to make sure that the public IP
    is always the VPN server's IP and not the device's.

    Discussion:

    It is unlikely that the adapter would be disabled in this way in the real world, but of course
    not impossible. However, this represents a class of tests which disrupt the primary network
    adapter. Other types of disruption would be:

    * Ethernet cable pulled (see TestDNSDisruptCable)
    * Wi-Fi power disabled (see TestWindowsOSDNSDisruptWifiPower)
    * Wi-Fi network unavailable, e.g. walk out of range of Wi-Fi network.

    Weaknesses:

    None

    Scenarios:

    No restrictions.

    TODO:

    This class only disables the primary adapter. Would be good to try permutations like:

        * Disable all adapters
          * This opens up a class of behaviour tests of "what does my VPN do when I lose all
            connectivity but then get it back later"
        * Disable a secondary adapter
        * Disable all but the primary adapter

    This behaviour should be configurable from the test config.
    '''

    def __init__(self, devices, parameters):
        super().__init__(WindowsAdapterDisrupter, devices, parameters)
