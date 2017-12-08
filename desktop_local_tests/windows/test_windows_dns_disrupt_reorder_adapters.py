from desktop_local_tests.dns_during_disruption import DNSDuringDisruptionTestCase
from desktop_local_tests.windows.windows_reorder_adapters_disrupter import WindowsReorderAdaptersDisrupter

class TestWindowsDNSDisruptReorderAdapters(DNSDuringDisruptionTestCase):

    '''Summary:

    Test whether DNS leaks when the adapter order is changed.

    Details:

    This test will connect to VPN then swap the priority of the primary and secondary network
    adapters. Once the order is changed the test repeatedly makes DNS requests and checks whether
    the DNS request went to a non VPN DNS server

    Discussion:

    It's not 100% clear if, in the real world, adapters can change their order without user
    involvement. It is still however a good stress test of the application.

    On Windows adapter order is determined by the interface metric. It can be manually set but
    otherwise it is determined by the system by deciding how "good" an adapter is, e.g. what is the
    throughput. In theory that means metrics can change dynamically.

    Weaknesses:

    Currently uses dig to decide if DNS leaks. This isn't reliable for some VPN providers. Some
    providers intercept DNS upstream and change the destination DNS server to their own server.
    However dig will still report the server which it originally sent the request to.

    Scenarios:

    Requires two active adapters.

    TODO:

    Consider a variant which changes the network "Location". This is much more likely to be
    something a user might do.
    '''

    def __init__(self, devices, parameters):
        super().__init__(WindowsReorderAdaptersDisrupter, devices, parameters)
