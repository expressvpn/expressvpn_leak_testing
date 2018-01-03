import random
import string

from xv_leak_tools.exception import XVEx
from xv_leak_tools.log import L
from xv_leak_tools.test_components.firewall.firewall import Firewall
from xv_leak_tools.test_device.connector_helper import ConnectorHelper

class LinuxFirewall(Firewall):

    def __init__(self, device, config):
        super().__init__(device, config)
        self._connector_helper = ConnectorHelper(self._device)
        # Having a randomized test chain name is a cheap way of ensuring that two instances of this
        # class will never interfere with one another. Unlikely we'll ever need two but you never
        # know
        self._testing_chain_name = "xv_leak_testing_" + "".join(
            random.choice(string.ascii_uppercase) for _ in range(8))
        self._create_testing_chain()

    def __del__(self):
        self._delete_testing_chain()

    def _block_ip_args_rules(self, ip):
        return [
            [self._testing_chain_name, "-s", ip, "-j", "DROP"],
            [self._testing_chain_name, "-d", ip, "-j", "DROP"],
        ]

    def _chain_exists(self, chain):
        ret, _, _ = self._connector_helper.execute_command(["iptables", "-w", "--list", chain], root=True)
        return ret == 0

    def _create_chain(self, chain):
        L.debug("Creating iptables chain {}".format(chain))
        if self._chain_exists(chain):
            L.debug("iptables chain {} exists".format(chain))
            return
        self._connector_helper.check_command(["iptables", "-w", "-N", chain], root=True)

    def _delete_chain(self, chain):
        L.debug("Deleting iptables chain {}".format(chain))
        if not self._chain_exists(chain):
            L.debug("iptables chain {} doesn't exist".format(chain))
        self._connector_helper.check_command(["iptables", "-w", "-X", chain], root=True)

    def _rule_exists(self, rule_args):
        ret, _, _ = self._connector_helper.execute_command(["iptables", "-w", "-C"] + rule_args, root=True)
        return ret == 0

    def _create_rule(self, rule_args):
        L.debug("Creating iptables rule {}".format(rule_args))
        if self._rule_exists(rule_args):
            L.debug("iptables rule {} already exists".format(rule_args))

        self._connector_helper.check_command(["iptables", "-w", "-A"] + rule_args, root=True)

    def _delete_rule(self, rule_args):
        L.debug("Deleting iptables rule {}".format(rule_args))
        if not self._rule_exists(rule_args):
            L.debug("iptables rule {} doesn't exist".format(rule_args))
            return

        self._connector_helper.check_command(["iptables", "-w", "-D"] + rule_args, root=True)

    def _jump_rule_args(self, chain):
        return [chain, "-j", self._testing_chain_name]

    def _delete_testing_chain(self):
        # Flush all rules in our chain
        self._connector_helper.check_command(
            ["iptables", "-w", "-F", self._testing_chain_name], root=True)

        # Remove all references (jumps) to our chain
        L.debug("Cleaning up iptables testing chain")
        for source_chain in ["INPUT", "OUTPUT"]:
            self._delete_rule(self._jump_rule_args(source_chain))

        self._delete_chain(self._testing_chain_name)

    def _create_testing_chain(self):
        self._create_chain(self._testing_chain_name)

        for source_chain in ["INPUT", "OUTPUT"]:
            self._create_rule(self._jump_rule_args(source_chain))

    def block_ip(self, ip):
        rules = self._block_ip_args_rules(ip)
        for rule in rules:
            self._create_rule(rule)

    def unblock_ip(self, ip):
        rules = self._block_ip_args_rules(ip)
        for rule in rules:
            self._delete_rule(rule)

# I wanted to use iptc (https://github.com/ldx/python-iptables) but it was buggy so gave up.

    # def _delete_testing_chain(self):
    #     for source_chain in ["INPUT", "OUTPUT"]:
    #         jump_rule = iptc.Rule()
    #         jump_rule.create_target(self._testing_chain_name)
    #         chain = iptc.Chain(iptc.Table(iptc.Table.FILTER), source_chain)
    #         chain.delete_rule(jump_rule)

    #     chain = iptc.Chain(iptc.Table(iptc.Table.FILTER), self._testing_chain_name)
    #     chain.flush()
    #     chain.delete()

    # def _create_testing_chain(self):
    #     try:
    #         iptc.Table(iptc.Table.FILTER).create_chain(self._testing_chain_name)
    #     except iptc.ip4tc.IPTCError as ex:
    #         if 'Chain already exists' not in str(ex):
    #             raise XVEx("Unknown error when creating iptables chain: {}".format(ex))

    #     for source_chain in ["INPUT", "OUTPUT"]:
    #         jump_rule = iptc.Rule()
    #         jump_rule.create_target(self._testing_chain_name)
    #         if self._rule_exists(self._testing_chain_name, jump_rule):
    #             print("RULE EXISTS")
    #             continue
    #         chain = iptc.Chain(iptc.Table(iptc.Table.FILTER), source_chain)
    #         chain.insert_rule(jump_rule)

    # def block_ip(self, ip):
    #     chain = iptc.Chain(iptc.Table(iptc.Table.FILTER), self._testing_chain_name)

    #     inbound_rule = iptc.Rule()
    #     inbound_rule.src = ip
    #     inbound_rule.create_target("DROP")
    #     chain.insert_rule(inbound_rule)

    #     outbound_rule = iptc.Rule()
    #     outbound_rule.dst = ip
    #     outbound_rule.create_target("DROP")
    #     chain.insert_rule(outbound_rule)
