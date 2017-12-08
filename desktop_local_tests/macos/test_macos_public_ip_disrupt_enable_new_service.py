from desktop_local_tests.public_ip_during_disruption import PublicIPDuringDisruptionTestCase
from desktop_local_tests.macos.macos_enable_new_service_disrupter import MacOSEnableNewServiceDisrupter

class TestMacOSPublicIPDisruptEnableNewService(PublicIPDuringDisruptionTestCase):

    '''Summary:

    Tests whether traffic leaving the user's device has the public IP hidden when a higher priority
    network service becomes active after connecting.

    Details:

    The test first identifies the highest priority network service and disables it. It then
    connects to the VPN and re-enables that service. The test then queries a webpage to detect it's
    public IP.

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

    The time taken to perform each IP request is relatively long. Tests using IPResponder should be
    preferred over these tests.

    Scenarios:

    Requires two active network services.

    TODO:

    Add tests for inactive and newly created services.
    '''

    def __init__(self, devices, parameters):
        super().__init__(MacOSEnableNewServiceDisrupter, devices, parameters)
