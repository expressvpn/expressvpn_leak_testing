from desktop_local_tests.local_packet_capture_test_case_with_disrupter import LocalPacketCaptureTestCaseWithDisrupter
from desktop_local_tests.windows.windows_enable_new_adapter_disrupter import WindowsEnableNewAdapterDisrupter

class TestWindowsPacketCaptureDisruptEnableNewAdapter(LocalPacketCaptureTestCaseWithDisrupter):

    '''Summary:

    Tests whether traffic leaving the user's device leaks outside of the VPN tunnel when a higher
    priority network adapter becomes active after connecting.

    Details:

    The test first identifies the highest priority adapter and disables it. It then connects to the
    VPN and re-enables that adapter. The test looks for leaking traffic once the interface has been
    disabled.

    Discussion:

    There are several ways in which a adapter could become active after connect:

    * The adapter is "enabled" via Network Connections (in Control Panel)
    * The adapter is enabled but there's no connectivity, e.g. the Ethernet cable is unplugged or
      Wi-Fi isn't connected to a Wi-Fi network. We refer to this situation as the adapter having
      "no network".
    * The adapter never existed in the first place and is created after connect.

    This test uses the first method to disable/re-enable the adapter to test for leaks. The other
    two scenarios are valid test cases and should also be implemented.

    Weaknesses:

    Packet capture tests can be noisy. Traffic can be detected as a leak but in actual fact may not
    be. For example, traffic might go to a server owned by the VPN provider to re-establish
    connections. In general this test is best used for manual exploring leaks rather than for
    automation.

    Scenarios:

    Requires two active adapters.

    TODO:

    Add tests for inactive and newly created adapters.
    '''

    def __init__(self, devices, parameters):
        super().__init__(WindowsEnableNewAdapterDisrupter, devices, parameters)
