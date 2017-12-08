from desktop_local_tests.local_packet_capture_test_case_with_disrupter import LocalPacketCaptureTestCaseWithDisrupter
from desktop_local_tests.disrupter_cable import DisrupterCable

class TestPacketCaptureDisruptCable(LocalPacketCaptureTestCaseWithDisrupter):

    '''Summary:

    Test whether traffic leaks when the Ethernet cable is either removed or plugged in after
    connection.

    Details:

    The test is a manual test which prompts the user to unplug or plug in an Ethernet (depending
    on how the test is configured). The test looks for leaking traffic once the cable has been
    unplugged/plugged.

    Discussion:

    Since the test is manual, one could actually replace "Plug/Unplug Ethernet Cable" with any
    action they desire. We could have just created a test called TestPacketCaptureManualDisruption
    (or similar). The reason for specifically naming the test is just to catalog the type of test
    case we're interested in.

    If you're working with a VM then you can simulate pulling a cable by just disabling the network
    adapter on the host machine, e.g. with VMWare:

    VM Settings->Network Adapter N->Connect Network Adapter.

    Weaknesses:

    Packet capture tests can be noisy. Traffic can be detected as a leak but in actual fact may not
    be. For example, traffic might go to a server owned by the VPN provider to re-establish
    connections. In general this test is best used for manual exploring leaks rather than for
    automation.

    Scenarios:

    No restrictions.

    TODO:

    Automate this test when using a VM. We should be able to disconnect/reconnect the guest
    programmatically.
    '''

    def __init__(self, devices, parameters):
        super().__init__(DisrupterCable, devices, parameters)
