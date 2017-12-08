from desktop_local_tests.public_ip_during_disruption import PublicIPDuringDisruptionTestCase
from desktop_local_tests.windows.windows_reorder_adapters_disrupter import WindowsReorderAdaptersDisrupter

class TestWindowsPublicIPDisruptReorderAdapters(PublicIPDuringDisruptionTestCase):

    '''Summary:

    Tests whether traffic leaving the user's device has the public IP hidden when the adapter order
    is changed.

    Details:

    This test will connect to VPN then swap the priority of the primary and secondary network
    adapters. The test then queries a webpage to detect it's public IP.

    Discussion:

    It's not 100% clear if, in the real world, adapters can change their order without user
    involvement. It is still however a good stress test of the application.

    On Windows adapter order is determined by the interface metric. It can be manually set but
    otherwise it is determined by the system by deciding how "good" an adapter is, e.g. what is the
    throughput. In theory that means metrics can change dynamically.

    Weaknesses:

    The time taken to perform each IP request is relatively long. Tests using IPResponder should be
    preferred over these tests.

    Scenarios:

    Requires two active adapters.

    TODO:

    Consider a variant which changes the network "Location". This is much more likely to be
    something a user might do.
    '''

    def __init__(self, devices, parameters):
        super().__init__(WindowsReorderAdaptersDisrupter, devices, parameters)
