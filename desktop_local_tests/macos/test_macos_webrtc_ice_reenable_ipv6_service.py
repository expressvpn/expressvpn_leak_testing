import ipaddress
from desktop_local_tests.local_test_case import LocalTestCase
from desktop_local_tests.webrtc_ice_helper import WebRTCICEHelper
from xv_leak_tools.log import L
from xv_leak_tools.test_framework.test_case import SupportedParameter

class TestMacOSWebRTCICEReenableIPv6Service(LocalTestCase):

    '''Summary:

    Test whether WebRTC leaks IPv6 addresses when we reenable a network service which is known to
    have IPv6 available on it.

    Details:

    This test connects to the VPN then enables an network service with IPv6 enabled.

    The test page does not use a STUN/TURN server and thus will be unable to detect public IPv4
    addresses when behind NAT (which will be 99.9% of the time). However, it makes sense to check
    for public IPv6 addresses here as NAT is in general unnecessary for IPv6 and a user's public
    IPv6 address can be assigned directly to the local interface.

    Discussion:

    This test is viable in the real world. It's possible for network services to come and go whilst
    a user is connected to the VPN. For example, a user might plug in an ethernet cable whilst
    already connected to the VPN and the ethernet connection may have IPv6 available.

    Weaknesses:

    No specific weaknesses.

    Scenarios:

    * Only run on a system which has IPv6 available on some network service.
    * Try scenarios where the newly enabled IPv6 service has priority both above and below the
      primary service at time of connect.
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

    def __init__(self, devices, parameters):
        super().__init__(devices, parameters)
        self.ipv6_service = None

    def find_ipv6_service(self):
        services = self.localhost['network_tool'].network_services_in_priority_order()
        active_services = [service for service in services if service.active()]
        for service in active_services:
            if not service.ipv6_addresses():
                continue
            self.ipv6_service = service
        return self.ipv6_service

    def test(self):
        L.describe('Get the public IP addresses before VPN connect')
        public_ips_before_connect = self.localhost['ip_tool'].all_public_ip_addresses()

        # Sanity check: We should always have at least one IP address!
        self.assertNotEmpty(public_ips_before_connect, "Couldn't get public IP addresses")
        L.info("Public IP addresses before VPN connect are {}".format(public_ips_before_connect))

        L.describe('Find a service with an IPv6 address')
        ipv6_service = self.find_ipv6_service()
        self.assertIsNotNone(ipv6_service, "Couldn't find a service with an IPv6 address")

        L.describe('Disabled the service with IPv6')
        ipv6_service.disable()
        L.info("Disabled service {}".format(ipv6_service))

        L.describe('Open and connect the VPN application')
        self.localhost['vpn_application'].open_and_connect()

        L.describe('Reenable the IPv6 service')
        ipv6_service.enable()
        ipv6_service.wait_for_active(10)

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
                "Found public IPv4 {} in ICE IPs".format(ip))
            if ip.version == 6:
                for subnet in ipv6_subnets:
                    self.assertFalse(
                        ip in subnet,
                        "New IPv6 address {} is in {}".format(ip, subnet))

    def teardown(self):
        if self.ipv6_service:
            self.ipv6_service.enable()

        super().teardown()
