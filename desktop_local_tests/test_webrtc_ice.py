import ipaddress

from desktop_local_tests.local_test_case import LocalTestCase
from desktop_local_tests.webrtc_ice_helper import WebRTCICEHelper
from xv_leak_tools.log import L
from xv_leak_tools.test_framework.test_case import SupportedParameter

class TestWebRTCICE(LocalTestCase):

    '''Summary:

    Test whether WebRTC is leaking during regular operation of the VPN.

    Details:

    This test connects to the VPN then then performs a WebRTC leak test. It opens a local webpage
    which uses the javascript WebRTC APIs to query WebRTC (ICE) IP addresses. A leak is considered
    to occur if any of the IP addresses is public.

    The test page does not use a STUN/TURN server and thus will be unable to detect public IPv4
    addresses when behind NAT (which will be 99.9% of the time). However, it makes sense to check
    for public IPv6 addresses here as NAT is in general unnecessary for IPv6 and a user's public
    IPv6 address can be assigned directly to the local interface.

    Discussion:

    The test can be run in two modes, one where it doesn't grant the webpage WebRTC permissions (
    audio/video capture) and one where it does. Both scenarios are valid leak tests. The worse of
    the two is when leaks occur when no permissions are granted. When permissions are granted
    though the user should still expect to be able to use WebRTC enabled websites safely without
    exposing their public IPs.

    Weaknesses:

    Testing must be done carefully. Browser tabs must always be closed and reopened as most browsers
    cache WebRTC IPs otherwise.

    Scenarios:

    * Run with IPv6 available - the most likely leak case.

    TODO:

    * On MacOS and Linux, is it possible to get the system into a state where there's an IPv6
      address attached to an interface but there's no corresponding network service?
    '''

    @staticmethod
    def supported_parameters():
        return {
            'browser': SupportedParameter(
                required=True,
                docs='Browser to use to run WebRTC test'),
            'ask_perms': SupportedParameter(
                default=False,
                required=False,
                docs='Causes the WebRTC test page to ask for permissions to use audio and video '
                'capture'),
            'host_remotely': SupportedParameter(
                default=False,
                required=False,
                docs='Run the page on a public HTTPS domain'),
        }

    def test(self):
        L.describe('Get the public IP addresses before VPN connect')
        public_ips_before_connect = self.localhost['ip_tool'].all_public_ip_addresses()

        # Sanity check: We should always have at least one IP address!
        self.assertNotEmpty(public_ips_before_connect, "Couldn't get public IP addresses")
        L.info("Public IP addresses before VPN connect are {}".format(public_ips_before_connect))

        L.describe('Open and connect the VPN application')
        self.localhost['vpn_application'].open_and_connect()

        # TODO: YUCK! config[config]
        L.describe('Find IPs reported by WebRTC')
        webdriver = self.localhost['webdriver'].driver(self.parameters['browser'])
        webrtc_ice_checker = WebRTCICEHelper(
            self.localhost,
            webdriver,
            self.parameters['ask_perms'],
            self.parameters['host_remotely'])

        webrtc_ips = webrtc_ice_checker.webrtc_ips()

        L.info("Found the following WebRTC IPs: {}".format(webrtc_ips))

        L.describe(
            'Check IPv4 addresses reported by WebRTC are all unknown and IPv6 addresses are all '
            'private')

        for ip in webrtc_ips:
            if isinstance(ip, ipaddress.IPv6Network):
                self.assertTrue(
                    ip.is_private, "Found public IPv6 address {} in ICE IPs".format(ip))
            else:
                self.assertIsNotIn(
                    ip, public_ips_before_connect,
                    "Found public IP {} in ICE IPs".format(ip))
