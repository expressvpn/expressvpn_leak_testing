import math
import time

from desktop_local_tests.local_test_case import LocalTestCase
from xv_leak_tools.exception import XVEx
from xv_leak_tools.helpers import TimeUp
from xv_leak_tools.log import L

class LocalIPResponderTestCase(LocalTestCase):

    DEFAULT_CHECK_PERIOD = 120

    def __init__(self, devices, parameters):
        super().__init__(devices, parameters)
        self._check_period = parameters.get(
            'check_period', LocalIPResponderTestCase.DEFAULT_CHECK_PERIOD)

    def test_with_ip_responder(self):
        pass

    def query_ip_responder(self):
        try:
            ips_from_responder = self.localhost['ip_responder'].query()
            L.info("IP addresses used were {}".format(ips_from_responder))
            return ips_from_responder
        except XVEx as ex:
            L.info("No response from IP responder. No problem, will continue testing: {}".format(
                ex))
            return set()

    def test(self):
        public_ips_before_connect = self.localhost['ip_tool'].all_public_ip_addresses()
        L.info("Public IP addresses before VPN connect are {}".format(public_ips_before_connect))

        L.describe('Open and connect the VPN application')
        self.localhost['vpn_application'].open_and_connect()

        self.localhost['ip_responder'].start()

        # Derived classes can override this with whatever they want.
        self.test_with_ip_responder()

        L.describe("Wait {} seconds before stopping ip responder".format(self._check_period))
        timeup = TimeUp(self._check_period)
        while not timeup:
            L.info("Running IP responder tests for another {} seconds".format(
                math.ceil(timeup.time_left())))

            ips_from_responder = self.query_ip_responder()
            ip_intersection = ips_from_responder.intersection(public_ips_before_connect)
            self.assertEmpty(
                ip_intersection,
                "The following public IPs were detected {}".format(ip_intersection))
            # Don't over query the responder. The background thread will still be spamming the
            # server so we won't miss anything.
            time.sleep(5)

        self.localhost['ip_responder'].stop()

        # Get rid of the VPN else it can affect our ability to talk to the server
        self.localhost['vpn_application'].disconnect()
        self.localhost['vpn_application'].close()

        # Some VPN apps take a while to close which means, if they implement a firewall, the
        # responder can't be reached. Allow some time for the network to come back in this situation
        timeup = TimeUp(20)
        while not timeup:
            ips_from_responder = self.query_ip_responder()
            if ips_from_responder:
                break
            if timeup:
                raise XVEx("Couldn't do final query of IP responder to get IPs. Got no response.")

        if not ips_from_responder:
            L.info("No IP addresses detected")
        else:
            L.info("IP addresses used were {}".format(ips_from_responder))

        ip_intersection = ips_from_responder.intersection(public_ips_before_connect)
        self.assertEmpty(
            ip_intersection,
            "The following public IPs were detected: {}".format(ip_intersection))
