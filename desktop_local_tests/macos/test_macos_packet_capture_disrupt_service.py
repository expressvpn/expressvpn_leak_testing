from desktop_local_tests.local_packet_capture_test_case_with_disrupter import LocalPacketCaptureTestCaseWithDisrupter
from desktop_local_tests.macos.macos_service_disrupter import MacOSServiceDisrupter

class TestMacOSPacketCaptureDisruptService(LocalPacketCaptureTestCaseWithDisrupter):

    '''Summary:

    Tests whether traffic leaving the user's device leaks outside of the VPN tunnel when the network
    service is disabled.

    Details:

    This test will connect to VPN then disable the primary network service, which will be the one
    used to connect to the VPN. The test looks for leaking traffic once the service has been
    disabled.

    Discussion:

    This is one of a class of tests which disrupt the primary network service. Other types of
    disruption would be:

    * Ethernet cable pulled (see TestPacketCaptureDisruptCable)
    * Wi-Fi power disabled (see TestMacOSPublicIPDisruptWifiPower)
    * Wi-Fi network unavailable, e.g. walk out of range of Wi-Fi network.

    Disabling the service from System Preferences is somewhat pathological but the test covers a
    wider range of more realistic scenarios.

    Weaknesses:

    Packet capture tests can be noisy. Traffic can be detected as a leak but in actual fact may not
    be. For example, traffic might go to a server owned by the VPN provider to re-establish
    connections. In general this test is best used for manual exploring leaks rather than for
    automation.

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
        super().__init__(MacOSServiceDisrupter, devices, parameters)
