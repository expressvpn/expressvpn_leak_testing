import select
import socket
import threading
import time
import ipaddress
import random
import string

from xv_leak_tools.exception import XVEx
from xv_leak_tools.helpers import TimeUp
from xv_leak_tools.log import L
from xv_leak_tools.test_components.component import Component

class IPResponder(Component):

    def __init__(self, device, config):
        super().__init__(device, config)
        self._token = ''.join(
            random.choice(string.ascii_uppercase) for _ in range(16)).encode("ascii")
        self._server_address = None
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._query_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._stop_sending = None
        self._send_forever_thread = None
        self._packet_count = 1

        ip_responder_server = self._config.get('ip_responder_server', None)
        if ip_responder_server:
            self._set_server(ip_responder_server, self._config.get('ip_responder_port', 80))

    def _send_forever(self, interval=0.001):
        while not self._stop_sending.is_set():
            self.send(self._token + b'~' + str(self._packet_count).encode("ascii"))
            time.sleep(interval)
            self._packet_count += 1

    def _receive(self, timeout=1):
        L.debug("Listening on %s:%s" % self._query_sock.getsockname())
        ready = select.select([self._query_sock], [], {}, timeout)
        if not ready[0]:
            raise XVEx("Didn't get a response from IP responder server")
        data = self._query_sock.recvfrom(4096)[0]
        return set(ipaddress.ip_address(ip) for ip in data.decode().split())

    def _check_server(self):
        # Query the server first and make sure it's up
        try:
            self.query(timeout=1)
            L.info("IP Responder is up and running at {}:{}".format(*self._server_address))
        except XVEx:
            raise XVEx(
                "IP responder server isn't running at {}:{}. Please make sure you start "
                "it!".format(*self._server_address))

    def _set_server(self, server_ip, server_port):
        self._server_address = (server_ip, server_port)
        L.debug("IPResponder using server at {}:{}".format(*self._server_address))

    def teardown(self):
        self.stop()
        super().teardown()

    def start(self):
        L.debug('Starting IPResponder thread')
        if self._server_address is None:
            raise XVEx("Server address must be set before starting IPResponder")

        if self._send_forever_thread is not None:
            raise XVEx("IP Responder already started")

        self._check_server()
        self._stop_sending = threading.Event()
        self._send_forever_thread = threading.Thread(target=self._send_forever)
        self._send_forever_thread.start()

    def stop(self):
        L.debug('Stopping IPResponder thread')
        if self._send_forever_thread is None:
            return

        self._stop_sending.set()

        L.debug('Waiting for thread to die...')
        while self._send_forever_thread.is_alive():
            continue

        self._stop_sending = None
        self._send_forever_thread = None

    def send(self, token=None):
        token = token or self._token
        try:
            self._sock.sendto(token, self._server_address)
        except OSError:
            # Don't notify anyone about this. The use case of this class is to send a lot of traffic
            # so dropped packets don't matter. Indeed they are expected as some tests will cause the
            # network to drop.
            pass

    def query(self, timeout=10):
        L.debug("IPResponder getting IPs for {}".format(self._token.decode()))
        timeup = TimeUp(timeout)
        first_time_around = True
        while not timeup:
            try:
                if not first_time_around:
                    L.verbose("Trying to querying IP responder server again")
                else:
                    L.verbose("Querying IP responder server")
                    first_time_around = False

                self._query_sock.sendto(self._token + b'?', self._server_address)
                return self._receive()
            except (OSError, XVEx) as ex:
                # OSError happens if sendto fails (which probably means no network)
                # XVEx happens if there's no response to receive.
                L.warning("IP responder query failed: {}".format(ex))
                time.sleep(1)

        raise XVEx("Couldn't query IP Responder server")
