import random

from multiprocessing.pool import ThreadPool
from threading import Semaphore

from desktop_local_tests.local_packet_capture_test_case import LocalPacketCaptureTestCase
from xv_leak_tools.exception import XVEx
from xv_leak_tools.log import L

class TestDNSVanillaAggressivePacketCapture(LocalPacketCaptureTestCase):

    '''Summary:

    Test whether DNS leaks during regular VPN connection.

    Details:

    This tests makes lots of simultaneous DNS requests once the VPN is connected. It uses packet
    capture to check that none of those requests went outside of the VPN tunnel.

    Discussion:

    The test is very similar to TestDNSVanillaAggressive but checks for leaks via packet capture and
    not dig.

    Weaknesses:

    It is expected that DNS traffic goes through the VPN tunnel so this test does not look for
    traffic on the tunnel itself. This doesn't mean there aren't DNS leaks. It's entirely possible
    for traffic to leak through the tunnel by going to a public DNS server, e.g. 8.8.8.8. If it
    goes over the tunnel then it will be encrypted and have the user's IP hidden, but the request
    itself can end up on a logging DNS server.

    Scenarios:

    * Run on a system with DNS servers configured to be public IP addresses, e.g. 8.8.8.8.
    * Run on a system with DNS servers configured to be local IP addresses, e.g. 192.0.0.0/24. This
      is a common setup with home routers where the router acts as the DNS server.

    '''

    # TODO: Potentially make configurable
    HOSTNAMES = [
        'google.com', 'twitter.com', 'facebook.com', 'stackoverflow.com', 'yahoo.com', 'amazon.com',
    ]

    NUM_PROCESSES = 10

    def __init__(self, devices, parameters):
        super().__init__(devices, parameters)
        self.dns_servers_before_connect = []
        self.thread_pool = ThreadPool(processes=TestDNSVanillaAggressivePacketCapture.NUM_PROCESSES)
        self.results = []
        self.semaphore = Semaphore(value=0)

    def filter_packets(self, packets):
        packets = super().filter_packets(packets)
        # Note that this filter does a reverse match, i.e. we match against port 53 but keep just
        # those packets
        just_port_53_packets = self.traffic_filter.filter_traffic(packets, dst_port=53)[0]
        return just_port_53_packets

    def thread_should_exit(self):
        return self.semaphore.acquire(blocking=False)

    def do_dns_requests(self):
        while not self.thread_should_exit():
            try:
                hostname = random.choice(TestDNSVanillaAggressivePacketCapture.HOSTNAMES)
                self.localhost['dns_tool'].lookup(hostname)
            except XVEx as ex:
                L.debug("DNS lookup failed. Not considering this an error: {}".format(ex))

    def start_traffic_generation(self):
        L.info("Starting background DNS lookup threads")
        # TODO: Consider making this into a generic traffic generator.
        for _ in range(0, TestDNSVanillaAggressivePacketCapture.NUM_PROCESSES):
            self.results.append(self.thread_pool.apply_async(self.do_dns_requests))

    def stop_traffic_generation(self):
        L.info("Stopping background DNS lookup threads")
        for _ in range(0, TestDNSVanillaAggressivePacketCapture.NUM_PROCESSES):
            self.semaphore.release()

        # There is no result returned from check_dns, but .get() will propagate any exception
        # thrown by check_dns, which is what we want.
        for result in self.results:
            result.get()
