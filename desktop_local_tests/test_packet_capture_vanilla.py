from desktop_local_tests.local_packet_capture_test_case import LocalPacketCaptureTestCase

class TestPacketCaptureVanilla(LocalPacketCaptureTestCase):

    '''Summary:

    Test whether traffic leaks outside of the VPN tunnel during regular operation of the VPN.

    Details:

    This test connects to the VPN then starts packet capture to monitor all outgoing traffic from
    the device. It then checks to see if any traffic leaked outside of the VPN. The test is
    automatic and just runs for a fixed period of time specified by the 'check_period' parameter.

    Discussion:

    This test has no implementation as the base class handles everything. The only thing that needs
    to be done is specify the 'check_period' parameter in the test config. This determines how long
    the test will check the IP for.

    This is a vanilla test and makes no attempt to disrupt the VPN.

    Weaknesses:

    Packet capture tests can be noisy. Traffic can be detected as a leak but in actual fact may not
    be. For example, traffic might go to a server owned by the VPN provider to re-establish
    connections. In general this test is best used for manual exploring leaks rather than for
    automation.

    Scenarios:

    No restrictions.

    '''

    pass
