from desktop_local_tests.public_ip_during_disruption import PublicIPDuringDisruptionTestCase
from desktop_local_tests.macos.macos_reorder_services_disrupter import MacOSDNSReorderServicesDisrupter

class TestMacOSPublicIPDisruptReorderServices(PublicIPDuringDisruptionTestCase):

    '''Summary:

    Tests whether traffic leaving the user's device has the public IP hidden when the network
    service order is changed.

    Details:

    This test will connect to VPN then swap the priority of the primary and secondary network
    services. The test then queries a webpage to detect it's public IP.

    Discussion:

    It's not 100% clear if, in the real world, services can change their order without user
    involvement. It is still however a good stress test of the application.

    Weaknesses:

    The time taken to perform each IP request is relatively long. Tests using IPResponder should be
    preferred over these tests.

    Scenarios:

    Requires two active network services.

    TODO:

    Consider a variant which changes the network "Location". This is much more likely to be
    something a user might do.
    '''

    def __init__(self, devices, parameters):
        super().__init__(MacOSDNSReorderServicesDisrupter, devices, parameters)
