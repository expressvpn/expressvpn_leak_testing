from desktop_local_tests.local_ip_responder_test_case_with_disrupter import LocalIPResponderTestCaseWithDisrupter
from desktop_local_tests.macos.macos_interface_disrupter import MacOSInterfaceDisrupter

class TestMacOSIPResponderDisruptInterface(LocalIPResponderTestCaseWithDisrupter):

    '''Summary:

    Tests whether traffic leaving the user's device has the public IP hidden when the network
    interface is disabled.

    Details:

    This test will connect to VPN then disable the primary network service's interface, which will
    be the one used to connect to the VPN.

    This test uses a simple UDP client which spams UDP packets to a public server. The server logs
    the source IP of every packet. The test checks with the server to make sure that the public IP
    is always the VPN server's IP and not the device's.

    Discussion:

    This is a pathological test. It is unlikely that an interface would go down. It would likely
    need deliberate action from the user to cause this to happen. However, it's a useful stress test
    and certainly not impossible that applications in the wild could cause this to happen. At worst
    this is protection for developers who are using the VPN application.

    Weaknesses:

    None

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
