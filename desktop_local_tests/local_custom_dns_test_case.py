import asyncio
import math
import time

from multiprocessing.pool import ThreadPool

from desktop_local_tests.local_test_case import LocalTestCase
from xv_leak_tools.exception import XVEx
from xv_leak_tools.helpers import TimeUp
from xv_leak_tools.log import L

class LocalCustomDNSTestCase(LocalTestCase):

    DEFAULT_CHECK_PERIOD = 60

    def __init__(self, devices, parameters):
        super().__init__(devices, parameters)
        self._check_period = self.parameters.get(
            'check_period', LocalCustomDNSTestCase.DEFAULT_CHECK_PERIOD)
        self._background_threads = self.parameters.get('background_threads', 1)
        self._thread_pool = ThreadPool(processes=self._background_threads)
        self._thread_results = []
        self._stop_dns = True
        self._stop_dns_lock = asyncio.Lock()
        if 'dns_server' not in  self.parameters:
            raise XVEx("Must specify 'dns_server' in the parameters")
        self._dns_server = self.parameters['dns_server']
        self._hostname = 'xv_leak_test_there_is_no_way_this_domain_exists.com'
        self._failure = None

    def test_with_custom_dns(self):
        '''Override this to do whatever you like whilst we're firing off DNS requests to our custom
        DNS server'''
        pass

    def dns_check_main(self):
        while not self._stop_dns:
            result = self.localhost['dns_tool'].lookup(
                self._hostname, timeout=1, server=self._dns_server)[1]
            if result:
                self.set_failure(result)

    def start_checking_dns(self):
        self._stop_dns = False
        L.info("Starting {} background DNS threads".format(self._background_threads))
        for _ in range(0, self._background_threads):
            self._thread_results.append(self._thread_pool.apply_async(self.dns_check_main))

    def stop_checking_dns(self):
        self._stop_dns = True
        for result in self._thread_results:
            result.get()

    def set_failure(self, response):
        # No mutual exclusion here. Entirely possible for other threads to update this.
        # no issues. We don't (currently) care about picking up which thread failed when, just
        # care that one did.
        self._failure = response
        self.stop_checking_dns()

    def test(self):
        L.describe('Open and connect the VPN application')
        self.localhost['vpn_application'].open_and_connect()

        self.start_checking_dns()

        # This is a bit of a hack. If a VPN fails immediately, i.e. just allows custom DNS servers
        # then we'll know very quickly. Let's check for that before doing anything specific for the
        # test:
        time.sleep(2)

        self.assertIsNone(
            self._failure,
            "Managed to send DNS request our own DNS server. Got response {}.\n"
            "NOTE: This happened BEFORE we even did any custom testing. This means the provider"
            "doesn't protect against DNS requests being sent to custom servers".format(
                self._failure))

        # Derived classes can override this with whatever they want.
        self.test_with_custom_dns()

        L.describe("Wait {} seconds before stopping DNS tests".format(self._check_period))
        timeup = TimeUp(self._check_period)
        while not timeup:
            L.info("Running DNS tests for another {} seconds".format(
                math.ceil(timeup.time_left())))

            self.assertIsNone(
                self._failure,
                "Managed to send DNS request our own DNS server. Got response {}".format(
                    self._failure))
            time.sleep(1)

        self.stop_checking_dns()
