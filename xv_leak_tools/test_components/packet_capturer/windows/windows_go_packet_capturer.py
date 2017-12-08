import os
import random
import signal
import string
import subprocess
import time

from xv_leak_tools.exception import XVEx
from xv_leak_tools.helpers import TimeUp
from xv_leak_tools.log import L
from xv_leak_tools.object_parser import object_from_json_file
from xv_leak_tools.path import makedirs_safe, windows_real_path

class WindowsGoPacketCapturer:

    def __init__(self, device, interface):
        # TODO: This is a bit of a hack for Windows for now. Running the capturer as a daemon on
        # Windows and in Cygwin is a bit of a pain. For now we just use popen and bypass the whole
        # device and connector framework.
        if device.device_id() != 'localhost':
            raise XVEx(
                "Packet capture on Windows can currently only be done if the Windows device is the"
                "test orchestrator, i.e. the current device")

        self._device = device
        self._interface = interface
        self._capture_file = 'capture.{}.json'.format(self._interface)
        self._popen = None
        self._pid = None

    @staticmethod
    def _random_pid_file():
        return "xv_packet_capture_{}.pid".format(
            ''.join(random.choice(string.ascii_uppercase) for _ in range(10)))

    def _get_packets(self):
        dst = os.path.join(self._device.temp_directory(), self._capture_file)
        timeup = TimeUp(5)
        while not timeup:
            if os.path.exists(dst):
                break
            L.warning("Waiting for capture file to be written: {}".format(dst))
            time.sleep(1)

        if not os.path.exists(dst):
            raise XVEx("Couldn't get capture file from capture device")

        return object_from_json_file(dst, 'attribute')['data']

    def _find_windows_pid(self):
        pids = self._device.pgrep("xv_packet_capture.exe")
        for pid in pids:
            cmd_line = self._device.command_line_for_pid(pid)
            for arg in cmd_line:
                if self._capture_file in arg:
                    return pid
        raise XVEx("Couldn't find PID")

    def start(self):
        L.debug("Starting packet capture on interface {}".format(self._interface))
        if self._popen:
            raise XVEx("Packet capture already started!")

        binary = os.path.join(
            os.path.dirname(os.path.realpath(__file__)), "..", "bin", "xv_packet_capture.exe")

        os.path.join(self._device.temp_directory(), WindowsGoPacketCapturer._random_pid_file())

        binary = windows_real_path(binary)
        output_directory = windows_real_path(self._device.temp_directory())
        cmd = [
            'cmd.exe',
            '/c',
            binary,
            '-i', str(self._interface),
            '-o', output_directory,
            '-f', self._capture_file,
            '-m', 'windump',
            '--preserve',
            '--debug'
        ]

        stdout = os.path.join(self._device.temp_directory(), "{}.stdout".format(self._capture_file))
        stderr = os.path.join(self._device.temp_directory(), "{}.stderr".format(self._capture_file))

        # TODO: Check for errors once opened?
        L.debug("Starting packet capture: {}".format(cmd))
        makedirs_safe(self._device.temp_directory())
        with open(stdout, "w") as out, open(stderr, "w") as err:
            self._popen = subprocess.Popen(cmd, stdout=out, stderr=err)

        self._pid = self._find_windows_pid()

    def stop(self):
        L.debug("Stopping packet capture on interface {} and getting packets".format(
            self._interface))

        if not self._popen:
            raise XVEx("Packet capture not started!")

        old_handler = None
        def interrupt_func(_, __):
            L.debug("Ignoring interrupt in main process when killing packet capture")
            signal.signal(signal.SIGINT, old_handler)

        old_handler = signal.signal(signal.SIGINT, interrupt_func)

        # Requires https://github.com/alirdn/windows-kill
        subprocess.Popen(
            ['windows-kill', '-SIGINT', str(self._pid)],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        self._pid = None

        # self._popen.send_signal(2)
        self._popen.wait()
        self._popen = None
        return self._get_packets()
