from desktop_local_tests.local_packet_capture_test_case_with_disrupter import LocalPacketCaptureTestCaseWithDisrupter
from desktop_local_tests.windows.windows_reorder_adapters_disrupter import WindowsReorderAdaptersDisrupter

class TestWindowsPacketCaptureDisruptReorderAdapters(LocalPacketCaptureTestCaseWithDisrupter):

    '''Summary:

    Tests whether traffic leaving the user's device leaks outside of the VPN tunnel when the adapter
    order is changed.

    Details:

    This test will connect to VPN then swap the priority of the primary and secondary network
    adapters. The test looks for leaking traffic once the interface has been disabled.

    Discussion:

    It's not 100% clear if, in the real world, adapters can change their order without user
    involvement. It is still however a good stress test of the application.

    On Windows adapter order is determined by the interface metric. It can be manually set but
    otherwise it is determined by the system by deciding how "good" an adapter is, e.g. what is the
    throughput. In theory that means metrics can change dynamically.

    Weaknesses:

    Packet capture tests can be noisy. Traffic can be detected as a leak but in actual fact may not
    be. For example, traffic might go to a server owned by the VPN provider to re-establish
    connections. In general this test is best used for manual exploring leaks rather than for
    automation.

    Scenarios:

    Requires two active adapters.

    TODO:

    Consider a variant which changes the network "Location". This is much more likely to be
    something a user might do.
    '''

    def __init__(self, devices, parameters):
        super().__init__(WindowsReorderAdaptersDisrupter, devices, parameters)
