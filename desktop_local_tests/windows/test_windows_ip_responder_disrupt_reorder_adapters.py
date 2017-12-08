from desktop_local_tests.local_ip_responder_test_case_with_disrupter import LocalIPResponderTestCaseWithDisrupter
from desktop_local_tests.windows.windows_reorder_adapters_disrupter import WindowsReorderAdaptersDisrupter

class TestWindowsIPResponderDisruptReorderAdapters(LocalIPResponderTestCaseWithDisrupter):

    '''Summary:

    Tests whether traffic leaving the user's device has the public IP hidden when the network
    service is disabled.

    Details:

    This test will connect to VPN then disable the primary network service, which will be the one
    used to connect to the VPN.

    This test uses a simple UDP client which spams UDP packets to a public server. The server logs
    the source IP of every packet. The test checks with the server to make sure that the public IP
    is always the VPN server's IP and not the device's.

    Discussion:

    This is one of a class of tests which disrupt the primary network service. Other types of
    disruption would be:

    * Ethernet cable pulled (see TestDNSDisruptCable)
    * Wi-Fi power disabled (see TestMacOSDNSDisruptWifiPower)
    * Wi-Fi network unavailable, e.g. walk out of range of Wi-Fi network.

    Disabling the service from System Preferences is somewhat pathological but the test covers a
    wider range of more realistic scenarios.

    Weaknesses:

    None

    Scenarios:

    No restrictions.

    TODO:

    This class only downs the interface associated to the primary service. Would be good to try
    permutations like:

        * Disable all services
          * This opens up a class of behaviour tests of "what does my VPN do when I lose all
            connectivity but then get it back later"
        * Disable a secondary service
        * Disable all but primary service
        * Implement Wi-Fi unavailable tests

    This behaviour should be configurable from the test config.
    '''

    def __init__(self, devices, parameters):
        super().__init__(WindowsReorderAdaptersDisrupter, devices, parameters)
