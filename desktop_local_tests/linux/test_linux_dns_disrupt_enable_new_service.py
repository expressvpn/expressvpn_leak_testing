from desktop_local_tests.dns_during_disruption import DNSDuringDisruptionTestCase
from desktop_local_tests.linux.linux_enable_new_service_disrupter import LinuxEnableNewServiceDisrupter

class TestLinuxDNSDisruptEnableNewService(DNSDuringDisruptionTestCase):

    '''Summary:

    Test whether DNS leaks when a new, higher priority network service appears after the VPN has
    connected.

    Details:

    This test will connect to the VPN then enable a network service which is known to have a higher
    priority than the currently active network services. It will then make a DNS request and check
    whether there was a leak.

    Discussion:

    This test addresses a specific weakness in many VPNs. The common scenario is that a user is
    connected to their home router which provides it's own DNS server (often served itself by the
    ISP). The DNS server IP will this be a local IP, e.g. in the range 192.0.0.0/24. When the user
    connects, most VPN provides set the DNS servers for the primary network service on which the
    VPN connection is initiated. When the new service appears it's DNS server will still be set to
    the router. MacOS uses the DNS server of the highest priority network service for all DNS
    requests. Since most VPN applications allow local LAN traffic when connected this can lead to
    DNS requests leaking persistently out through the router.

    Weaknesses:

    * It might be better to perform lots of DNS requests rather than a single lookup.

    Scenarios:

    * Run on a system with DNS servers configured to be public IP addresses, e.g. 8.8.8.8.
    * Run on a system with DNS servers configured to be local IP addresses, e.g. 192.0.0.0/24. This
      is a common setup with home routers where the router acts as the DNS server.

    TODO:

    * Expand the scenario to test for all types of leaks.

    '''

    def __init__(self, devices, config):
        super().__init__(LinuxEnableNewServiceDisrupter, devices, config)
