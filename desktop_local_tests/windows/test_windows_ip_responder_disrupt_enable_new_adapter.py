from desktop_local_tests.local_ip_responder_test_case_with_disrupter import LocalIPResponderTestCaseWithDisrupter
from desktop_local_tests.windows.windows_enable_new_adapter_disrupter import WindowsEnableNewAdapterDisrupter

class TestWindowsIPResponderDisruptEnableNewAdapter(LocalIPResponderTestCaseWithDisrupter):

    '''Summary:

    Tests whether traffic leaving the user's device has the public IP hidden when a higher
    priority network adapter becomes active after connecting.

    Details:

    The test first identifies the highest priority adapter and disables it. It then connects to the
    VPN and re-enables that adapter.

    This test uses a simple UDP client which spams UDP packets to a public server. The server logs
    the source IP of every packet. The test checks with the server to make sure that the public IP
    is always the VPN server's IP and not the device's.

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

    None

    Scenarios:

    Requires two active adapters.

    TODO:

    Add tests for inactive and newly created adapters.
    '''

    def __init__(self, devices, parameters):
        super().__init__(WindowsEnableNewAdapterDisrupter, devices, parameters)
