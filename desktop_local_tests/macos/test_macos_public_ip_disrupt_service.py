from desktop_local_tests.public_ip_during_disruption import PublicIPDuringDisruptionTestCase
from desktop_local_tests.macos.macos_service_disrupter import MacOSServiceDisrupter

class TestMacOSPublicIPDisruptService(PublicIPDuringDisruptionTestCase):

    '''Summary:

    Tests whether traffic leaving the user's device has the public IP hidden when the network
    service is disabled.

    Details:

    This test will connect to VPN then disable the primary network service, which will be the one
    used to connect to the VPN. The test then queries a webpage to detect it's public IP.

    Discussion:

    This is one of a class of tests which disrupt the primary network service. Other types of
    disruption would be:

    * Ethernet cable pulled (see TestDNSDisruptCable)
    * Wi-Fi power disabled (see TestMacOSDNSDisruptWifiPower)
    * Wi-Fi network unavailable, e.g. walk out of range of Wi-Fi network.

    Disabling the service from System Preferences is somewhat pathological but the test covers a
    wider range of more realistic scenarios.

    Weaknesses:

    The time taken to perform each IP request is relatively long. Tests using IPResponder should be
    preferred over these tests.

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
