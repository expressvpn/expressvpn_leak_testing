from xv_leak_tools.log import L
from desktop_local_tests.local_test_case import LocalTestCase

# TODO: Rewrite this test to use PublicIPDuringDisruptionTestCase but when the disruption is
# trivial.
class TestPublicIPAddress(LocalTestCase):
    '''Summary:

    Test whether public IP addresses leak.

    Details:

    This is the simplest of VPN tests. Checks whether the VPN hides your public IPv4 and IPv6
    addresses. This is tested by simply visiting IPv4 and IPv6 sites and checking what IP was used
    for the connection.

    Discussion:

    None

    Weaknesses:

    * Sites only report a single IP per IP-version. It's possible for a system to have multiple
      network cards or multiple IPs per network card. This test would not catch issues here.

    Scenarios:

    No restrictions.
    '''

    def test(self):
        L.describe('Get the public IP addresses before VPN connect')
        public_ips_before_connect = self.localhost['ip_tool'].all_public_ip_addresses()

        # Sanity check: We should always have at least one IP address!
        self.assertNotEmpty(public_ips_before_connect, "Couldn't get public IP addresses")

        L.info("Public IP addresses before VPN connect are {}".format(public_ips_before_connect))

        L.describe('Open and connect the VPN application')
        self.localhost['vpn_application'].open_and_connect()

        L.describe('Get the public IP addresses after VPN connect')
        public_ips_after_connect = self.localhost['ip_tool'].all_public_ip_addresses()

        L.info("Public IP addresses after VPN connect are {}".format(public_ips_after_connect))

        L.describe('Expect public IP addresses after VPN connect to have all changed')

        unchanged_ips = set(public_ips_before_connect).intersection(public_ips_after_connect)
        self.assertEmpty(
            unchanged_ips, "These IPs did not get changed after connection to VPN {}".format(
                unchanged_ips))
