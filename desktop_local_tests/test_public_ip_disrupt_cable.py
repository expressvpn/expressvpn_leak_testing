from desktop_local_tests.public_ip_during_disruption import PublicIPDuringDisruptionTestCase
from desktop_local_tests.disrupter_cable import DisrupterCable

class TestPublicIPDisruptCable(PublicIPDuringDisruptionTestCase):

    '''Summary:

    Test whether the device's public IP is exposed when the Ethernet cable is either removed or
    plugged in after connection.

    Details:

    The test is a manual test which prompts the user to unplug or plug in an Ethernet (depending
    on how the test is configured). Once the cable has been unplugged/plugged the test repeatedly
    checks the device's public IPv4 and IPv6 addresses by visiting a webpage designed to report
    those IPs.

    Discussion:

    Since the test is manual, one could actually replace "Plug/Unplug Ethernet Cable" with any
    action they desire. We could have just created a test called TestDNSManualDisruption (or
    similar). The reason for specifically naming the test is just to catalog the type of test case
    we're interested in.

    If you're working with a VM then you can simulate pulling a cable by just disabling the network
    adapter on the host machine, e.g. with VMWare:

    VM Settings->Network Adapter N->Connect Network Adapter.

    Weaknesses:

    The time taken to perform each IP request is relatively long. Tests using IPResponder should be
    preferred over these tests.

    Scenarios:

    No restrictions.
    '''

    def __init__(self, devices, parameters):
        super().__init__(DisrupterCable, devices, parameters)
