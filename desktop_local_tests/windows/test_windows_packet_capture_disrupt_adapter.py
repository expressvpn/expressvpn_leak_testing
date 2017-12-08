from desktop_local_tests.local_packet_capture_test_case_with_disrupter import LocalPacketCaptureTestCaseWithDisrupter
from desktop_local_tests.windows.windows_adapter_disrupter import WindowsAdapterDisrupter

class TestWindowsPacketCaptureDisruptAdapter(LocalPacketCaptureTestCaseWithDisrupter):

    '''Summary:

    Tests whether traffic leaving the user's device leaks outside of the VPN tunnel when the network
    adapter is disabled.

    Details:

    This test will connect to VPN then disable the primary network adapter. The test looks for
    leaking traffic once the interface has been disabled.

    Discussion:

    It is unlikely that the adapter would be disabled in this way in the real world, but of course
    not impossible. However, this represents a class of tests which disrupt the primary network
    adapter. Other types of disruption would be:

    * Ethernet cable pulled (see TestDNSDisruptCable)
    * Wi-Fi power disabled (see TestWindowsOSDNSDisruptWifiPower)
    * Wi-Fi network unavailable, e.g. walk out of range of Wi-Fi network.

    Weaknesses:

    Packet capture tests can be noisy. Traffic can be detected as a leak but in actual fact may not
    be. For example, traffic might go to a server owned by the VPN provider to re-establish
    connections. In general this test is best used for manual exploring leaks rather than for
    automation.

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
