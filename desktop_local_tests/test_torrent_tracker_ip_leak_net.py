import time
import ipaddress

from desktop_local_tests.ip_leak_net_helper import IPLeakNetHelper
from desktop_local_tests.local_test_case import LocalTestCase
from xv_leak_tools.helpers import TimeUp
from xv_leak_tools.log import L
from xv_leak_tools.exception import XVEx

# TODO: Test with
# client open/shut
# browser tab refresh vs reopen

class TestTorrentTrackerIPLeakNet(LocalTestCase):

    '''Summary:

    Test whether Torrent clients are leaking during regular operation of the VPN.

    Details:

    This test connects to the VPN then then performs a bit torrent leak test. The test currently
    uses ipleak.net to detect the leak. This uses a custom bit torrent tracker to detect what IPs
    the client is announcing and thus can detect IPv4 and IPv6 leaks.

    Discussion:

    This test doesn't test that torrent uploads/downloads are leaking. This can be easily tested
    with arbitrary traffic but should also be tested with a specific torrent test for completeness.
    The test is only interested in spotting torrent clients announcing the user's public IP
    addresses when they're connected to the VPN.

    Torrent clients are known to cache IPs. Thus if you have a client open before the VPN connects
    then there's almost definitely going to be a leak. This is, in our opinion, a flaw with the
    torrent clients and should be addresses there. This test

    This test only concerns itself with traditional torrent trackers. Nothing has yet been done
    with regards to DHTs. It's expected that behaviour will be the same, but not confirmed. Note
    that the use of magnets is irrelevant and standard torrent files are equivalent to magnets for
    the purpose of leak testing.

    Weaknesses:

    * Torrent clients are hard to automate without manually driving UI interaction, thus these
      tests are inherently manually for now.
    * The test page may be caching IPs so care must be taken to open the page only after connecting
      to VPN.

    Scenarios:

    * Run with/without IPv6 available
    * Run with the client pre-opened before connecting to the VPN (clients are known to cache IPs)
    * Run with the client opened after connecting to the VPN

    TODO:

    * Let's build our own test page which gives results as simple JSON (done - just needs
      integrating).
    * Let's make our page work slightly differently. In order to automate torrent clients more
      easily, let's make the tracker links specific to the client rather than randomly generated.
      We can thus pre-add torrent magnets to the the clients and simply open them in order to
      trigger the test (which can be easily automated).
    * Let's also add support for DHTs somehow.
    '''

    def __init__(self, devices, parameters):
        super().__init__(devices, parameters)
        self.torrent_client = self.parameters['torrent_client']
        self.torrent_client_preopened = self.parameters['torrent_client_preopened']
        self._webdriver = None

    def test(self):
        L.describe('Get the public IP addresses before VPN connect')
        public_ips_before_connect = self.localhost['ip_tool'].all_public_ip_addresses()

        # Sanity check: We should always have at least one IP address!
        self.assertNotEmpty(public_ips_before_connect, "Couldn't get public IP addresses")
        L.info("Public IP addresses before VPN connect are {}".format(public_ips_before_connect))

        self.localhost['torrent_client'].set_client(self.torrent_client)

        # We're assuming the client is already closed. I think that's ok.
        if self.torrent_client_preopened:
            self.localhost['torrent_client'].open()

        L.describe('Open and connect the VPN application')
        self.localhost['vpn_application'].open_and_connect()

        self._webdriver = self.localhost['webdriver'].driver(self.parameters['browser'])
        ip_leak_helper = IPLeakNetHelper(self._webdriver)

        L.describe('Open ipleak.net page')
        ip_leak_helper.load_page()

        L.describe('Get the torrent magnet link from ipleak.net')
        magnet_link = ip_leak_helper.get_magnet_link()
        L.info("Got magnet link {}".format(magnet_link))

        L.describe('Add the torrent magnet to the torrent client')
        self.localhost['torrent_client'].add_torrent(magnet_link)

        L.describe("Check the reported torrent IPs aren't public")

        ipv6_subnets = [ipaddress.ip_interface((ip, 64)).network
                        for ip in public_ips_before_connect if ip.version == 6]

        timeup = TimeUp(20)
        reported_ips = set()
        while not timeup:
            L.info('Checking webpage contents for leaked torrent IPs')
            reported_ips.update(ip_leak_helper.get_reported_torrent_ips())

            for ip in reported_ips:
                self.assertIsNotIn(
                    ip, public_ips_before_connect,
                    "Torrent tracker found a public IP: {}".format(ip))

                if ip.version == 6:
                    for subnet in ipv6_subnets:
                        self.assertFalse(
                            ip in subnet,
                            "IPv6 address {} is in {}".format(ip, subnet))

            if reported_ips:
                L.info("Found IPs {} but none were public".format(reported_ips))
            else:
                L.info('Found no IPs')

            # Pause a little each run to give IPs a chance to report.
            time.sleep(1)

        if not reported_ips:
            raise XVEx("The torrent client didn't report any IP addresses at all")

    def teardown(self):
        self._webdriver.close()
        super().teardown()
