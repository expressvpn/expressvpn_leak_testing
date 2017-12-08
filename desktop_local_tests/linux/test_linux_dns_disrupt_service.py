from desktop_local_tests.dns_during_disruption import DNSDuringDisruptionTestCase
from desktop_local_tests.linux.linux_service_disrupter import  LinuxServiceDisrupter

class TestLinuxDNSDisruptService(DNSDuringDisruptionTestCase):

    '''Summary:

    Test whether DNS leaks when the network service is disrupted.

    Details:

    This test will connect to VPN then disable the primary network service which will be the one
    used to connect to the VPN. Once the app notices the disruption the test will reenable the
    network service then make DNS requests to try to generate a DNS leak.

    Discussion:

    This test is one of many variants. We specifically are interested here in the behaviour when
    the network service is disabled.

    This test may not make sense for all VPN applications. It will only work on applications which
    detect the network loss and make the user aware of it. If the app hides this information from
    the user then there's no prompt at which to reenable the network interface.

    Some applications might simply move to a failed state or disconnect, rather than trying to
    reconnect. However it's still reasonable to ask whether such apps leak when this happens.

    Weaknesses:

    The main weakness is the dependence on the app alerting the user there was an issue. This could
    potentially be remedied by reenabling the interface after a specific time period. However, it is
    very difficult to predict what the "correct" time period would be for a specific app. Running
    the test multiple times with incremental time periods of say up to 1 or 2 minutes could help
    here, but this would lead to very long running tests.

    Scenarios:

    * Run on a system with DNS servers configured to be public IP addresses, e.g. 8.8.8.8.
    * Run on a system with DNS servers configured to be local IP addresses, e.g. 192.0.0.0/24. This
      is a common setup with home routers where the router acts as the DNS server.
    * Run on a system with just one network service
    * Run on a system with several network services

    TODO:

    This class only handles primary service. Would be good to try permutations like:
        * All services
        * Secondary service
        * All but primary

    This behavour should be configurable from the test config.
    '''

    def __init__(self, devices, parameters):
        super().__init__(LinuxServiceDisrupter, devices, parameters)
