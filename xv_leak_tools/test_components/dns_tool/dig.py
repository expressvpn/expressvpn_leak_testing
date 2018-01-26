import ipaddress
import math
import re

from xv_leak_tools.exception import XVEx
from xv_leak_tools.log import L
from xv_leak_tools.network.common import RE_IPV4_ADDRESS
from xv_leak_tools.test_device.connector_helper import ConnectorHelper

class Dig: # pylint: disable=too-few-public-methods

    # Server line looks like:
    # ;; SERVER: 8.8.8.8#53(8.8.8.8)
    PROG_DIG_SERVER = re.compile(r";; SERVER:\s*({}).*".format(RE_IPV4_ADDRESS))

    # Answers look like:
    # google.com.     39  IN  A   216.58.200.14
    PROG_DIG_ANSWER = re.compile(r"[^\s]+\s+\d+\s+[A-Z]+\s+[A-Z]+\s+({})".format(RE_IPV4_ADDRESS))

    def __init__(self, device):
        self._connector_helper = ConnectorHelper(device)

    def _execute(self, cmd):
        return self._connector_helper.check_command(cmd)

    @staticmethod
    def _parse_answers(lines):
        ips = []
        for line in lines:
            if line.strip() == "":
                break
            matches = Dig.PROG_DIG_ANSWER.match(line)
            if not matches:
                continue
            ips.append(ipaddress.ip_address(matches.group(1)))

        return ips

    @staticmethod
    def _parse_output(output):
        server = None
        lines = output.splitlines()
        for line in lines:
            matches = Dig.PROG_DIG_SERVER.match(line)
            if not matches:
                continue
            server = matches.group(1)
            break

        if server is None:
            raise XVEx("Couldn't parse dig output: {}".format(output))

        ips = []
        for iline, line in enumerate(lines):
            if 'ANSWER SECTION' not in line:
                continue
            ips = Dig._parse_answers(lines[iline+1:])
            break

        if len(ips) == 0:
            raise XVEx("dig failed to return any IPs. Output was: {}".format(output))

        return ipaddress.ip_address(server), ips

    # TODO: The timeout here isn't reliable. The process can lock. Let's wrap this with a Popen
    # and just hard kill the process if it time's out. Note that this will be fiddly for remote
    # execution!
    def lookup(self, hostname, timeout, server=None):
        # dig doesn't like floats for timeout
        timeout = int(math.ceil(timeout))
        if server:
            cmd = ['dig', "+time={}".format(timeout), hostname, "@{}".format(server)]
        else:
            cmd = ['dig', "+time={}".format(timeout), hostname]

        # Prevent the output from being empty
        stdout = None
        while not stdout:
            stdout = self._execute(cmd)[0]
            if not stdout:
                L.verbose("dig output was empty; doing another lookup.")

        L.verbose("dig output: {}".format(stdout))
        return Dig._parse_output(stdout)
