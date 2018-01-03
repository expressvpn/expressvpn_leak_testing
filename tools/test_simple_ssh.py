#!/usr/bin/env python3

# TODO: Remove this once the sys.path.append is gone
# pylint: disable=wrong-import-position

import os
import sys

# TODO: I think we solve this problem by making a proper pip module
# Add the root so we can import xv_leak_tools
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..'))

from xv_leak_tools.log import L
from xv_leak_tools.test_device.simple_ssh_connector import SimpleSSHConnector
# from xv_leak_tools.test_device.static_device_discoverer import StaticDeviceDiscoverer

L.configure({
    'trace': {
        'level': L.VERBOSE,
    },
    'describe': {
        'file_format': None,
    },
    'report': {
        'file_format': None,
    },
})

CONNECTOR = SimpleSSHConnector(
    ips=['10.163.0.1'], username='root',
    ssh_key=os.path.expanduser('~/.ssh/id_rsa'),
    ssh_password=None)

RET, STDOUT, STDERR = CONNECTOR.execute(['ls'])

print(RET)
print("--------------")
print(STDOUT)
print("--------------")
print(STDERR)
