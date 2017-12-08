from desktop_local_tests.public_ip_during_disruption import PublicIPDuringDisruptionTestCase
from desktop_local_tests.windows.windows_enable_new_adapter_disrupter import WindowsEnableNewAdapterDisrupter

class TestWindowsPublicIPDisruptEnableNewAdapter(PublicIPDuringDisruptionTestCase):

    '''Summary:

    Tests whether traffic leaving the user's device has the public IP hidden when a higher priority
    network adapter becomes active after connecting.

    Details:

    The test first identifies the highest priority adapter and disables it. The test then queries a
    webpage to detect it's public IP.

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

    The time taken to perform each IP request is relatively long. Tests using IPResponder should be
    preferred over these tests.

    Scenarios:

    Requires two active adapters.

    TODO:

    Add tests for inactive and newly created adapters.
    '''

    def __init__(self, devices, parameters):
        super().__init__(WindowsEnableNewAdapterDisrupter, devices, parameters)
