from desktop_local_tests.dns_during_disruption import DNSDuringDisruptionTestCase
from desktop_local_tests.macos.macos_interface_disrupter import MacOSInterfaceDisrupter

class TestMacOSDNSDisruptInterface(DNSDuringDisruptionTestCase):

    '''Summary:

    Test whether DNS leaks when the network interface is disabled.

    Details:

    This test will connect to VPN then disable the primary network service's interface, which will
    be the one used to connect to the VPN. Once the interface is disabled the test repeatedly makes
    DNS requests and checks whether the DNS request went to a non VPN DNS server

    Discussion:

    This is a pathological test. It is unlikely that an interface would go down. It would likely
    need deliberate action from the user to cause this to happen. However, it's a useful stress test
    and certainly not impossible that applications in the wild could cause this to happen. At worst
    this is protection for developers who are using the VPN application.

    Weaknesses:

    Currently uses dig to decide if DNS leaks. This isn't reliable for some VPN providers. Some
    providers intercept DNS upstream and change the destination DNS server to their own server.
    However dig will still report the server which it originally sent the request to.

    Scenarios:

    No restrictions.

    TODO:

    This class only downs the interface associated to the primary service. Would be good to try
    permutations like:

        * Down interface for all services
          * This opens up a class of behaviour tests of "what does my VPN do when I lose all
            connectivity but then get it back later"
        * Down interface for a secondary service
        * Down interface for all but primary

    This behaviour should be configurable from the test config.
    '''

    def __init__(self, devices, parameters):
        super().__init__(MacOSInterfaceDisrupter, devices, parameters)
