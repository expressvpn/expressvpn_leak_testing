from desktop_local_tests.dns_during_disruption import DNSDuringDisruptionTestCase
from desktop_local_tests.disrupter_cable import DisrupterCable

class TestDNSDisruptCable(DNSDuringDisruptionTestCase):

    '''Summary:

    Test whether DNS leaks when the Ethernet cable is either removed or plugged in after connection.

    Details:

    The test is a manual test which prompts the user to unplug or plug in an Ethernet (depending
    on how the test is configured). Once the cable has been unplugged/plugged the test repeatedly
    makes DNS requests and checks whether the DNS request went to a non VPN DNS server.

    Discussion:

    Since the test is manual, one could actually replace "Plug/Unplug Ethernet Cable" with any
    action they desire. We could have just created a test called TestDNSManualDisruption (or
    similar). The reason for specifically naming the test is just to catalog the type of test case
    we're interested in.

    If you're working with a VM then you can simulate pulling a cable by just disabling the network
    adapter on the host machine, e.g. with VMWare:

    VM Settings->Network Adapter N->Connect Network Adapter.

    Weaknesses:

    Currently uses dig to decide if DNS leaks. This isn't reliable for some VPN providers. Some
    providers intercept DNS upstream and change the destination DNS server to their own server.
    However dig will still report the server which it originally sent the request to.

    Scenarios:

    No restrictions.

    TODO:

    Automate this test when using a VM. We should be able to disconnect/reconnect the guest
    programmatically.
    '''

    def __init__(self, devices, parameters):
        super().__init__(DisrupterCable, devices, parameters)
