from desktop_local_tests.local_packet_capture_test_case_with_disrupter import LocalPacketCaptureTestCaseWithDisrupter
from desktop_local_tests.macos.macos_enable_new_service_disrupter import MacOSEnableNewServiceDisrupter

class TestMacOSPacketCaptureDisruptEnableNewService(LocalPacketCaptureTestCaseWithDisrupter):

    '''Summary:

    Tests whether traffic leaving the user's device leaks outside of the VPN tunnel when a higher
    priority network service becomes active after connecting.

    Details:

    The test first identifies the highest priority network service and disables it. It then connects
    to the VPN and re-enables that service. The test looks for leaking traffic once the new service
    has been enabled.

    Discussion:

    There are several ways in which a service could become active after connect:

    * The service is "enabled" via System Preferences
    * Service is enabled but there's no connectivity, e.g. the Ethernet cable is unplugged or Wi-Fi
      isn't connected to a Wi-Fi network. We refer to this situation as the service being
      "inactive".
    * The service never existed in the first place and is created after connect.

    This test uses the first method to disable/reenable the service to test for leaks. The other two
    scenarios are valid test cases and should also be implemented.

    Weaknesses:

    Packet capture tests can be noisy. Traffic can be detected as a leak but in actual fact may not
    be. For example, traffic might go to a server owned by the VPN provider to re-establish
    connections. In general this test is best used for manual exploring leaks rather than for
    automation.

    Scenarios:

    Requires two active network services.

    TODO:

    Add tests for inactive and newly created services.
    '''

    def __init__(self, devices, parameters):
        super().__init__(MacOSEnableNewServiceDisrupter, devices, parameters)
