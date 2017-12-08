from desktop_local_tests.dns_during_disruption import DNSDuringDisruptionTestCase
from desktop_local_tests.windows.windows_enable_new_adapter_disrupter import WindowsEnableNewAdapterDisrupter

class TestWindowsDNSDisruptEnableNewAdapter(DNSDuringDisruptionTestCase):

    '''Summary:

    Test whether DNS leaks when a higher priority network adapter becomes active after connecting.

    Details:

    The test first identifies the highest priority adapter and disables it. It then
    connects to the VPN and re-enables that adapter. Once the adapter is active the test repeatedly
    makes DNS requests and checks whether the DNS request went to a non VPN DNS server

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

    Currently uses dig to decide if DNS leaks. This isn't reliable for some VPN providers. Some
    providers intercept DNS upstream and change the destination DNS server to their own server.
    However dig will still report the server which it originally sent the request to.

    Scenarios:

    Requires two active adapters.

    TODO:

    Add tests for inactive and newly created adapters.
    '''

    def __init__(self, devices, parameters):
        super().__init__(WindowsEnableNewAdapterDisrupter, devices, parameters)
