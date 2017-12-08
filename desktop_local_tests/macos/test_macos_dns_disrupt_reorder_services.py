from desktop_local_tests.dns_during_disruption import DNSDuringDisruptionTestCase
from desktop_local_tests.macos.macos_reorder_services_disrupter import MacOSDNSReorderServicesDisrupter

class TestMacOSDNSDisruptReorderServices(DNSDuringDisruptionTestCase):

    '''Summary:

    Test whether DNS leaks when the network service order is changed.

    Details:

    This test will connect to VPN then swap the priority of the primary and secondary network
    services. Once the order is changed the test repeatedly makes DNS requests and checks whether
    the DNS request went to a non VPN DNS server

    Discussion:

    It's not 100% clear if, in the real world, services can change their order without user
    involvement. It is still however a good stress test of the application.

    Weaknesses:

    Currently uses dig to decide if DNS leaks. This isn't reliable for some VPN providers. Some
    providers intercept DNS upstream and change the destination DNS server to their own server.
    However dig will still report the server which it originally sent the request to.

    Scenarios:

    Requires two active network services.

    TODO:

    Consider a variant which changes the network "Location". This is much more likely to be
    something a user might do.
    '''

    def __init__(self, devices, parameters):
        super().__init__(MacOSDNSReorderServicesDisrupter, devices, parameters)
