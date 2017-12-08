from desktop_local_tests.local_ip_responder_test_case_with_disrupter import LocalIPResponderTestCaseWithDisrupter
from desktop_local_tests.disrupter_cable import DisrupterCable

class TestIPResponderDisruptCable(LocalIPResponderTestCaseWithDisrupter):

    '''Summary:

    Tests whether traffic leaving the user's device has the public IP hidden when the Ethernet cable
    is either removed or plugged in after connection.

    Details:

    The test is a manual test which prompts the user to unplug or plug in an Ethernet (depending on
    how the test is configured).

    This test uses a simple UDP client which spams UDP packets to a public server. The server logs
    the source IP of every packet. The test checks with the server to make sure that the public IP
    is always the VPN server's IP and not the device's.

    Discussion:

    Since the test is manual, one could actually replace "Plug/Unplug Ethernet Cable" with any
    action they desire. We could have just created a test called TestDNSManualDisruption (or
    similar). The reason for specifically naming the test is just to catalog the type of test case
    we're interested in.

    If you're working with a VM then you can simulate pulling a cable by just disabling the network
    adapter on the host machine, e.g. with VMWare:

    VM Settings->Network Adapter N->Connect Network Adapter.

    Weaknesses:

    None

    Scenarios:

    No restrictions.

    TODO:

    Automate this test when using a VM. We should be able to disconnect/reconnect the guest
    programmatically.

    '''

    def __init__(self, devices, parameters):
        super().__init__(DisrupterCable, devices, parameters)
