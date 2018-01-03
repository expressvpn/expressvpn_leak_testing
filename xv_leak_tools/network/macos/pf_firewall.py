# Considered using https://pypi.python.org/pypi/py-pf/0.1.4 for this but it's out of date and no
# longer seems to work - at least on modern versions of macOS.

# Useful reference manual for pf: https://murusfirewall.com/Documentation/OS%20X%20PF%20Manual.pdf

import os
import random
import re
import string
import tempfile

from xv_leak_tools.exception import XVEx
from xv_leak_tools.helpers import is_root_user
from xv_leak_tools.log import L
from xv_leak_tools.process import check_subprocess, XVProcessException

class PFCtl:

    PROG_TOKEN = re.compile("Token : ([0-9]+)")

    def __init__(self, anchor_name=None, no_disable=False):
        if anchor_name is None:
            anchor_name = PFCtl._random_anchor_name()

        self._anchor_name = anchor_name
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

        self._ensure_anchor_is_present()

    def __del__(self):
        if self._no_disable:
            return
        self._ensure_anchor_is_removed()
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
    def _rewrite_root_rules(rules):
        rules_file = PFCtl._create_rules_file(rules)

        PFCtl._pfctl(['-Fr'])
        PFCtl._pfctl(['-f', rules_file])
        L.debug("Rewrote root pfctl rules")

    @staticmethod
    def _random_anchor_name():
        return "xv_leak_test_{}".format(
            "".join(random.choice(string.ascii_uppercase) for _ in range(10)))

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
    def flush_state():
        PFCtl._pfctl(['-Fs'])

    def _ensure_anchor_is_present(self):
        rules = PFCtl._read_root_rules()
        new_rules = []
        for rule in rules:
            if "xvpn" in rule:
                # Ensure we always put the leak testing rules before xvpn ones.
                # TODO: This isn't vendor agnostic. We should make it so.
                new_rules.append("anchor \"{}\" all".format(self._anchor_name))
            new_rules.append(rule)
            if self._anchor_name in rule:
                L.debug("Leak test anchor {} already present in rules".format(self._anchor_name))
                return

        PFCtl._rewrite_root_rules(new_rules)

    def _ensure_anchor_is_removed(self):
        rules = PFCtl._read_root_rules()
        new_rules = []
        need_update = False
        for rule in rules:
            if self._anchor_name not in rule:
                new_rules.append(rule)
            else:
                need_update = True

        if not need_update:
            L.debug("Leak test anchor {} wasn't found. No need to remove".format(self._anchor_name))
            return

        PFCtl._rewrite_root_rules(new_rules)

    def set_rules(self, rules):
        rules_file = PFCtl._create_rules_file(rules)
        PFCtl._pfctl(['-a', self._anchor_name, '-f', rules_file])
        PFCtl.flush_state()

    def clear_rules(self):
        PFCtl._pfctl(['-a', self._anchor_name, '-F', 'all'])
        PFCtl.flush_state()
