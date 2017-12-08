# Considered using https://pypi.python.org/pypi/py-pf/0.1.4 for this but it's out of date and no
# longer seems to work - at least on modern versions of macOS.

# Useful reference manual for pf: https://murusfirewall.com/Documentation/OS%20X%20PF%20Manual.pdf

import os
import re
import tempfile

from xv_leak_tools.exception import XVEx
from xv_leak_tools.helpers import is_root_user
from xv_leak_tools.log import L
from xv_leak_tools.process import check_subprocess, XVProcessException

# TODO: Should be a component
class PFCtl:

    LEAK_TEST_ANCHOR = 'xv_leak_test'
    PROG_TOKEN = re.compile("Token : ([0-9]+)")

    def __init__(self, no_disable=False):
        self._no_disable = no_disable
        self._token = None
        if self._no_disable:
            self._pfctl(['-e'])
        else:
            lines = self._pfctl(['-E'])[1].splitlines()
            for line in lines:
                match = PFCtl.PROG_TOKEN.match(line)
                if not match:
                    continue
                self._token = match.group(1)
                L.debug("Got pfctl reference {}".format(self._token))
            if not self._token:
                raise XVEx("Couldn't parse token from pfctl output:\n {}".format("\n".join(lines)))

    def __del__(self):
        if self._no_disable:
            return
        L.debug("Releasing pfctl reference {}".format(self._token))
        try:
            self._pfctl(['-X', self._token])
        except XVProcessException as ex:
            # This can happen as some providers will aggressively tear down the firewall when they
            # disconnect (using pfctl -d) and thus remove our reference (token) to the firewall.
            L.warning("Failed to terminate pf firewall: {}".format(ex))

    @staticmethod
    def _pfctl(cmd):
        if not is_root_user():
            raise XVEx("root required to manipulate pf firewall rules")
        cmd = ['pfctl'] + cmd
        L.debug("Executing pfctl command: {}".format(" ".join(cmd)))
        return check_subprocess(cmd)

    @staticmethod
    def _read_root_rules():
        ignore_lines = [
            "No ALTQ support in kernel",
            "ALTQ related functions disabled",
        ]

        rules = []
        lines = PFCtl._pfctl(['-sr'])[0].splitlines()
        for line in lines:
            for ignore_line in ignore_lines:
                if ignore_line not in line:
                    rules.append(line)
                    break
        return rules

    @staticmethod
    def _create_rules_file(rules):
        filehandle, path = tempfile.mkstemp(suffix='_pf_rules.conf', prefix='xv_leak_test_rules_')
        with os.fdopen(filehandle, 'w') as _file:
            for rule in rules:
                _file.write("{}\n".format(rule))
        L.debug("Wrote pf file {} with rules:\n{}".format(path, rules))
        return path

    @staticmethod
    def ensure_leak_test_anchor_present():
        rules = PFCtl._read_root_rules()
        for rule in rules:
            if PFCtl.LEAK_TEST_ANCHOR in rule:
                L.debug("Leak test anchor {} already present in rules".format(
                    PFCtl.LEAK_TEST_ANCHOR))
                return

        rules.append("anchor \"{}\" all".format(PFCtl.LEAK_TEST_ANCHOR))
        rules_file = PFCtl._create_rules_file(rules)

        PFCtl._pfctl(['-Fr'])
        PFCtl._pfctl(['-f', rules_file])
        L.debug("Rewrote root pfctl rules")

    @staticmethod
    def flush_state():
        PFCtl._pfctl(['-Fs'])

    @staticmethod
    def set_leak_test_rules(rules):
        PFCtl.ensure_leak_test_anchor_present()
        rules_file = PFCtl._create_rules_file(rules)
        PFCtl._pfctl(['-a', PFCtl.LEAK_TEST_ANCHOR, '-f', rules_file])
        PFCtl.flush_state()

    @staticmethod
    def clear_leak_test_rules():
        PFCtl._pfctl(['-a', PFCtl.LEAK_TEST_ANCHOR, '-F', 'all'])
        PFCtl.flush_state()
