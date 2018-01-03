#!/usr/bin/env python3

import os
import sys

# TODO: I think we solve this problem by making a proper pip module
# Add the root so we can import xv_leak_tools
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..'))

import fake_device
from xv_leak_tools.log import L
from xv_leak_tools.test_components.firewall.linux.linux_firewall import LinuxFirewall
from xv_leak_tools.test_components.firewall.macos.macos_firewall import MacOSFirewall

L.configure({
    'trace': {
        'level': L.DEBUG,
    },
    'describe': {
        'file_format': None,
    },
    'report': {
        'file_format': None,
    },
})

lf = MacOSFirewall(fake_device.get_fake_device(), {})
lf.block_ip("8.8.8.8")
lf.unblock_ip("8.8.8.8")
