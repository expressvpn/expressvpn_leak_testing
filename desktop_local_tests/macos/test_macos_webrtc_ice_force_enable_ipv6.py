import ipaddress
from desktop_local_tests.local_test_case import LocalTestCase
from desktop_local_tests.webrtc_ice_helper import WebRTCICEHelper
from xv_leak_tools.log import L
from xv_leak_tools.test_framework.test_case import SupportedParameter

class TestMacOSWebRTCICEForceEnableIPv6(LocalTestCase):

    '''Summary:

    Test whether WebRTC leaks IPv6 addresses when we forcibly enable IPv6 on all network services
    after connect.

    Details:

    This test connects to the VPN then iterates over all active network services and forcibly
    enables IPv6 on the service (by setting it to "Automatic"). It then performs a WebRTC leak test
    by opening a local webpage which uses the javascript WebRTC APIs to query WebRTC (ICE) IP
    addresses. A leak is considered to occur if any of the IP addresses is public.

    The test page does not use a STUN/TURN server and thus will be unable to detect public IPv4
    addresses when behind NAT (which will be 99.9% of the time). However, it makes sense to check
    for public IPv6 addresses here as NAT is in general unnecessary for IPv6 and a user's public
    IPv6 address can be assigned directly to the local interface.

    Discussion:

    VPN applications protect against IPv6 leaks and WebRTC leaks in many different ways. One known
    solution is to alter the IPv6 settings for network services.

    This test is a stress test around this around. It is valid for any VPN provider but results may
    differ depending on how the provider implements IPv6 WebRTC leak protection. It's unlikely in
    the real world that a user would deliberately reenable IPv6 on a network service manually,
    however this test can give insights into potential leaks in this area.

    Weaknesses:

    No specific weaknesses.

    Scenarios:

    * Only run on a system which has IPv6 available on some network service.
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

    # TODO: We should really preserve the state of IPv6 and teardown nicely.
    def enable_ipv6_on_all_active_services(self):
        services = self.localhost['network_tool'].network_services_in_priority_order()
        active_services = [service for service in services if service.active()]
        for active_service in active_services:
            active_service.enable_ipv6()

    def test(self):
        L.describe('Get the public IP addresses before VPN connect')
        public_ips_before_connect = self.localhost['ip_tool'].all_public_ip_addresses()

        # Sanity check: We should always have at least one IP address!
        self.assertNotEmpty(public_ips_before_connect, "Couldn't get public IP addresses")
        L.info("Public IP addresses before VPN connect are {}".format(public_ips_before_connect))

        L.describe('Open and connect the VPN application')
        self.localhost['vpn_application'].open_and_connect()

        L.describe('Forcibly enable IPv6 on all active network services')
        self.enable_ipv6_on_all_active_services()

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
            'Check IPv4 addresses reported by WebRTC are all unknown and IPv6 '
            'addresses are in a different subnet')

        ipv6_subnets = [ipaddress.ip_interface((ip, 64)).network
                        for ip in public_ips_before_connect if ip.version == 6]
        for ip in webrtc_ips:
            self.assertIsNotIn(
                ip, public_ips_before_connect,
                "Found public IP {} in ICE IPs".format(ip))
            if ip.version == 6:
                for subnet in ipv6_subnets:
                    self.assertFalse(
                        ip in subnet,
                        "New IPv6 address {} is in {}".format(ip, subnet))
