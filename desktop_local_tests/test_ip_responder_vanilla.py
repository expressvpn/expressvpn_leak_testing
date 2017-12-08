from desktop_local_tests.local_ip_responder_test_case import LocalIPResponderTestCase

class TestIPResponderVanilla(LocalIPResponderTestCase):

    '''Summary:

    Tests whether traffic leaving the user's device has the public IP hidden.

    Details:

    This test uses a simple UDP client which spams UDP packets to a public server. The server logs
    the source IP of every packet. The test checks with the server to make sure that the public IP
    is always the VPN server's IP and not the device's.

    Discussion:

    This test has no implementation as the base class handles everything. The only thing that needs
    to be done is specify the 'check_period' parameter in the test config. This determines how long
    the test will check the IP for.

    This is a vanilla test and makes no attempt to disrupt the VPN.

    Weaknesses:

    None

    Scenarios:

    No restrictions.

    '''

    pass
