# This class is very hacky for now. Only IP blocking has been tested aggressively as it's all we
# use. We use netsh advfirewall for managing the firewall. This is deprecated in favour of
# Powershell. For now we'll use this as we haven't implemented a Powershell wrapper yet.

# Some useful netsh advfirewall links
# https://serverfault.com/questions/415622/how-can-i-use-netsh-to-find-a-rule-using-a-pattern

# There is an alternative powershell approach, search for things like
#
# Get-Command -Module NetSecurity
# NetSh Advfirewall set allprofiles state off
# NetSh Advfirewall set allrprofiles state on
# Netsh Advfirewall show allprofiles

import random
import re
import string

from xv_leak_tools.log import L
from xv_leak_tools.process import check_subprocess
from xv_leak_tools.path import windows_real_path

class WindowsAdvFirewall:

    RULE_PREFIX = 'xv_leak_test_'
    ALLOW_RULE_PREFIX = RULE_PREFIX + 'allow_'
    BLOCK_RULE_PREFIX = RULE_PREFIX + 'block_'

    PROG_RULE_NAME = re.compile(r'Rule Name:\s*(.*)')

    @staticmethod
    def _generate_rule_name():
        return "{}{}".format(WindowsAdvFirewall.RULE_PREFIX, ''.join(
            random.choice(string.ascii_uppercase) for _ in range(10)))

    @staticmethod
    def list_xv_rules():
        rules = []
        stdout = check_subprocess(
            ['netsh', 'advfirewall', 'firewall', 'show', 'rule', 'name=all'])[0]

        for line in stdout.splitlines():
            matches = WindowsAdvFirewall.PROG_RULE_NAME.match(line)
            if not matches:
                continue
            name = matches.group(1)
            if WindowsAdvFirewall.RULE_PREFIX not in name:
                continue
            rules.append(name)

        return rules

    @staticmethod
    def describe_rule(name):
        # TODO: Probably don't need this
        out = check_subprocess(
            ['netsh', 'advfirewall', 'firewall', 'show', 'rule', "name={}".format(name)])[0]
        return out.splitlines()

    @staticmethod
    def delete_xv_rules():
        for rule in WindowsAdvFirewall.list_xv_rules():
            WindowsAdvFirewall.delete_rule(rule)

    @staticmethod
    def block_all_outbound_traffic():
        L.info('Blocking all outbound traffic')
        check_subprocess([
            'netsh', 'advfirewall', 'set', 'allprofiles', 'firewallpolicy',
            'blockinbound,blockoutbound'])

    @staticmethod
    def allow_all_outbound_traffic():
        L.info('Allowing all outbound traffic')
        check_subprocess([
            'netsh', 'advfirewall', 'set', 'allprofiles', 'firewallpolicy',
            'blockinbound,allowoutbound'])

    @staticmethod
    def set_rule_enable(name, enabled):
        enable = 'yes' if enabled else 'no'
        check_subprocess([
            'netsh', 'advfirewall', 'firewall', 'set', 'rule', "name={}".format(name), 'new',
            "enable={}".format(enable)])

    @staticmethod
    def enable_rule(name):
        L.info("Enabling firewall rule {}".format(name))
        WindowsAdvFirewall.set_rule_enable(name, True)

    @staticmethod
    def disable_rule(name):
        L.info("Disabling firewall rule {}".format(name))
        WindowsAdvFirewall.set_rule_enable(name, False)

    @staticmethod
    def delete_rule(name):
        L.info("Deleting firewall rule {}".format(name))
        cmd = ['netsh', 'advfirewall', 'firewall', 'delete', 'rule', "name={}".format(name)]
        check_subprocess(cmd)

    @staticmethod
    def create_rule(action, **kwargs):
        rule_name = WindowsAdvFirewall._generate_rule_name()
        cmd = [
            'netsh',
            'advfirewall',
            'firewall',
            'add',
            'rule',
            "name={}".format(rule_name),
            "action={}".format(action),
            "profile=any",
            "interfacetype=any",
        ]

        for key, value in list(kwargs.items()):
            cmd.append("{}={}".format(key, value))

        L.debug("Creating firewall rule with command {}".format(cmd))
        check_subprocess(cmd)
        return rule_name

    @staticmethod
    def allow_application(full_path, direction="out"):
        full_path = windows_real_path(full_path)
        L.info("Creating firewall rule to block application {}".format(full_path))
        return WindowsAdvFirewall.create_rule("allow", program=full_path, direction=direction)

    @staticmethod
    def block_application(full_path, direction="out"):
        full_path = windows_real_path(full_path)
        L.info("Creating firewall rule to block application {}".format(full_path))
        return WindowsAdvFirewall.create_rule("block", program=full_path, direction=direction)

    @staticmethod
    def block_ip(ip, direction="out"):
        return WindowsAdvFirewall.create_rule("blocK", remoteip=ip, direction=direction)
