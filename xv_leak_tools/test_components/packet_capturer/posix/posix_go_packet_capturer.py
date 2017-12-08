import os
import random
import string
import tempfile
import time

from xv_leak_tools import tools_root
from xv_leak_tools.exception import XVEx
from xv_leak_tools.helpers import TimeUp
from xv_leak_tools.log import L
from xv_leak_tools.object_parser import object_from_json_file
from xv_leak_tools.test_device.connector_helper import ConnectorHelper

class PosixGoPacketCapturer:

    def __init__(self, device, interface):
        self._device = device
        self._connector_helper = ConnectorHelper(self._device)
        self._interface = interface
        self._capture_file = 'capture.{}.json'.format(self._interface)
        self._pid_file = None

    def _binary_location(self):
        here_relative = os.path.relpath(os.path.dirname(os.path.realpath(__file__)), tools_root())
        return os.path.join(
            self._device.tools_root(), here_relative, '..', 'bin', "xv_packet_capture")

    def _get_packets(self):
        # TODO: This highlights a weakness in the framework. I can't pull to my local device
        # because I don't know where to pull to! Just pulling to a temp file for now
        src = os.path.join(self._device.temp_directory(), self._capture_file)
        file_, dst = tempfile.mkstemp(
            prefix="xv_leak_test_", suffix="_{}".format(self._capture_file))
        os.close(file_)
        os.remove(dst)

        timeup = TimeUp(5)
        while not timeup:
            try:
                self._device.connector().pull(src, dst)
                break
            except XVEx:
                L.warning("Waiting for capture file to be written: {}".format(src))
                time.sleep(1)

        if not os.path.exists(dst):
            raise XVEx("Couldn't get capture file from capture device")

        packets = object_from_json_file(dst, 'attribute')
        return packets['data']

    @staticmethod
    def _random_pid_file():
        return "xv_packet_capture_{}.pid".format(
            ''.join(random.choice(string.ascii_uppercase) for _ in range(10)))

    def start(self):
        L.debug("Starting packet capture on interface {}".format(self._interface))

        if self._pid_file:
            raise XVEx("Packet capture already started!")

        # TODO: Use PID file
        self._pid_file = os.path.join(
            self._device.temp_directory(), PosixGoPacketCapturer._random_pid_file())

        cmd = [
            '/usr/local/bin/daemon',
            '-o', os.path.join(self._device.temp_directory(), 'daemon.out'),
            '--',
            self._binary_location(),
            '-i', self._interface,
            '-o', self._device.temp_directory(),
            '-f', 'capture.{}.json'.format(self._interface),
            '--preserve',
            '--debug'
        ]
        self._connector_helper.check_command(cmd, root=True)

    def stop(self):
        L.debug("Stopping packet capture on interface {} and getting packets".format(
            self._interface))

        if not self._pid_file:
            raise XVEx("Packet capture not started!")

        # TODO: Switch to pid file kill
        cmd = ['killall', '-SIGINT', 'xv_packet_capture']
        self._connector_helper.check_command(cmd, root=True)

        self._pid_file = None
        return self._get_packets()
