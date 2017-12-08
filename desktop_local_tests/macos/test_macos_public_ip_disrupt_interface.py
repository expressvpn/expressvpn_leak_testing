from desktop_local_tests.public_ip_during_disruption import PublicIPDuringDisruptionTestCase
from desktop_local_tests.macos.macos_interface_disrupter import MacOSInterfaceDisrupter

class TestMacOSPublicIPDisruptInterface(PublicIPDuringDisruptionTestCase):

    '''Summary:

    Tests whether traffic leaving the user's device has the public IP hidden when the network
    interface is disabled.

    Details:

    This test will connect to VPN then disable the primary network service's interface, which will
    be the one used to connect to the VPN. The test then queries a webpage to detect it's
    public IP.

    Discussion:

    This is a pathological test. It is unlikely that an interface would go down. It would likely
    need deliberate action from the user to cause this to happen. However, it's a useful stress test
    and certainly not impossible that applications in the wild could cause this to happen. At worst
    this is protection for developers who are using the VPN application.

    Weaknesses:

    The time taken to perform each IP request is relatively long. Tests using IPResponder should be
    preferred over these tests.

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
