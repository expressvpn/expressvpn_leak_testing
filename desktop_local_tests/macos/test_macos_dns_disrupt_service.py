from desktop_local_tests.dns_during_disruption import DNSDuringDisruptionTestCase
from desktop_local_tests.macos.macos_service_disrupter import MacOSServiceDisrupter

class TestMacOSDNSDisruptService(DNSDuringDisruptionTestCase):

    '''Summary:

    Test whether DNS leaks when the network service is disabled.

    Details:

    This test will connect to VPN then disable the primary network service, which will be the one
    used to connect to the VPN. Once the service is disabled the test repeatedly makes DNS
    requests and checks whether the DNS request went to a non VPN DNS server

    Discussion:

    This is one of a class of tests which disrupt the primary network service. Other types of
    disruption would be:

    * Ethernet cable pulled (see TestDNSDisruptCable)
    * Wi-Fi power disabled (see TestMacOSDNSDisruptWifiPower)
    * Wi-Fi network unavailable, e.g. walk out of range of Wi-Fi network.

    Disabling the service from System Preferences is somewhat pathological but the test covers a
    wider range of more realistic scenarios.

    Weaknesses:

    Currently uses dig to decide if DNS leaks. This isn't reliable for some VPN providers. Some
    providers intercept DNS upstream and change the destination DNS server to their own server.
    However dig will still report the server which it originally sent the request to.

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
