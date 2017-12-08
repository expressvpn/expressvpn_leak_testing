from desktop_local_tests.dns_during_disruption import DNSDuringDisruptionTestCase
from desktop_local_tests.macos.macos_enable_new_service_disrupter import MacOSEnableNewServiceDisrupter

class TestMacOSDNSDisruptEnableNewService(DNSDuringDisruptionTestCase):

    '''Summary:

    Test whether DNS leaks when a higher priority network service becomes active after connecting.

    Details:

    The test first identifies the highest priority network service and disables it. It then
    connects to the VPN and re-enables that service. Once the service is active the test repeatedly
    makes DNS requests and checks whether the DNS request went to a non VPN DNS server

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

    Currently uses dig to decide if DNS leaks. This isn't reliable for some VPN providers. Some
    providers intercept DNS upstream and change the destination DNS server to their own server.
    However dig will still report the server which it originally sent the request to.

    Scenarios:

    Requires two active network services.

    TODO:

    Add tests for inactive and newly created services.
    '''

    def __init__(self, devices, parameters):
        super().__init__(MacOSEnableNewServiceDisrupter, devices, parameters)
