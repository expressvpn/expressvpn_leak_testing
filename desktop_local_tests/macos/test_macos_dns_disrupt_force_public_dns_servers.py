from desktop_local_tests.dns_during_disruption import DNSDuringDisruptionTestCase
from desktop_local_tests.macos.macos_dns_force_public_dns_servers_disrupter import MacOSDNSForcePublicDNSServersDisrupter

class TestMacOSDNSForcePublicDNSServers(DNSDuringDisruptionTestCase):

    '''Summary:

    Test whether DNS leaks when we forcibly set the DNS servers of the primary network service to
    use a public DNS server after connect.

    Details:

    The test connects to the VPN then sets the DNS server on the primary network service to a public
    IP (e.g. 8.8.8.8) Once the service is active the test repeatedly makes DNS requests and checks
    whether the DNS request went to a non VPN DNS server

    If the system believes the DNS server is some public IP, e.g. 8.8.8.8, then it might attempt to
    send DNS requests to this server. They would still be encrypted through the VPN tunnel,
    however requests would be seen by a third party. This is still a privacy leak.

    Discussion:

    This is a somewhat pathological test, in that it is unlikely a user would do this manually after
    connect. However, it is an interesting stress test as it tests the strength of a VPN
    application's firewalls.

    In the real world this type of leak could occur if an application chooses to use it's own DNS
    server(s) and not the system ones.

    Weaknesses:

    Currently uses dig to decide if DNS leaks. This isn't reliable for some VPN providers. Some
    providers intercept DNS upstream and change the destination DNS server to their own server.
    However dig will still report the server which it originally sent the request to.

    Scenarios:

    No restrictions.

    TODO:

    * Write a simpler test which just does dig @8.8.8.8 and doesn't change the DNS servers at all.
    * Write a test which sets the global DNS server but doesn't touch any network services' DNS
      servers.
    '''

    def __init__(self, devices, parameters):
        super().__init__(MacOSDNSForcePublicDNSServersDisrupter, devices, parameters)
