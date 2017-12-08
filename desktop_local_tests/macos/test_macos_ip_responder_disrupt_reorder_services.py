from desktop_local_tests.local_ip_responder_test_case_with_disrupter import LocalIPResponderTestCaseWithDisrupter
from desktop_local_tests.macos.macos_reorder_services_disrupter import MacOSDNSReorderServicesDisrupter

class TestMacOSIPResponderDisruptReorderServices(LocalIPResponderTestCaseWithDisrupter):

    '''Summary:

    Tests whether traffic leaving the user's device has the public IP hidden when the network
    service order is changed.

    Details:

    This test will connect to VPN then swap the priority of the primary and secondary network
    services.

    This test uses a simple UDP client which spams UDP packets to a public server. The server logs
    the source IP of every packet. The test checks with the server to make sure that the public IP
    is always the VPN server's IP and not the device's.

    Discussion:

    It's not 100% clear if, in the real world, services can change their order without user
    involvement. It is still however a good stress test of the application.

    Weaknesses:

    None

    Scenarios:

    Requires two active network services.

    TODO:

    Consider a variant which changes the network "Location". This is much more likely to be
    something a user might do.
    '''

    def __init__(self, devices, parameters):
        super().__init__(MacOSDNSReorderServicesDisrupter, devices, parameters)
