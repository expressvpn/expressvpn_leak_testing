from desktop_local_tests.local_packet_capture_test_case_with_disrupter import LocalPacketCaptureTestCaseWithDisrupter
from desktop_local_tests.macos.macos_interface_disrupter import MacOSInterfaceDisrupter

class TestMacOSPacketCaptureDisruptInterface(LocalPacketCaptureTestCaseWithDisrupter):

    '''Summary:

    Tests whether traffic leaving the user's device leaks outside of the VPN tunnel when the network
    interface is disabled.

    Details:

    This test will connect to VPN then disable the primary network service's interface, which will
    be the one used to connect to the VPN. The test looks for leaking traffic once the interface
    has been disabled.

    Discussion:

    This is a pathological test. It is unlikely that an interface would go down. It would likely
    need deliberate action from the user to cause this to happen. However, it's a useful stress test
    and certainly not impossible that applications in the wild could cause this to happen. At worst
    this is protection for developers who are using the VPN application.

    Weaknesses:

    Packet capture tests can be noisy. Traffic can be detected as a leak but in actual fact may not
    be. For example, traffic might go to a server owned by the VPN provider to re-establish
    connections. In general this test is best used for manual exploring leaks rather than for
    automation.

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
