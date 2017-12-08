from desktop_local_tests.dns_during_disruption import DNSDuringDisruptionTestCase
from desktop_local_tests.windows.windows_adapter_disrupter import WindowsAdapterDisrupter

class TestWindowsDNSDisruptAdapter(DNSDuringDisruptionTestCase):

    '''Summary:

    Test whether DNS leaks when the network adapter is disabled.

    Details:

    This test will connect to VPN then disable the primary network adapter. Once the adapter is
    disabled the test repeatedly makes DNS requests and checks whether the DNS request went to a non
    VPN DNS server

    Discussion:

    It is unlikely that the adapter would be disabled in this way in the real world, but of course
    not impossible. However, this represents a class of tests which disrupt the primary network
    adapter. Other types of disruption would be:

    * Ethernet cable pulled (see TestDNSDisruptCable)
    * Wi-Fi power disabled (see TestWindowsOSDNSDisruptWifiPower)
    * Wi-Fi network unavailable, e.g. walk out of range of Wi-Fi network.

    Weaknesses:

    Currently uses dig to decide if DNS leaks. This isn't reliable for some VPN providers. Some
    providers intercept DNS upstream and change the destination DNS server to their own server.
    However dig will still report the server which it originally sent the request to.

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
