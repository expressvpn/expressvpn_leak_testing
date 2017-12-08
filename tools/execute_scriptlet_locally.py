#!/usr/bin/env python3

# TODO: Remove this once the sys.path.append is gone
# pylint: disable=wrong-import-position

import argparse
import os
import sys

# TODO: I think we solve this problem by making a proper pip module
# Add the root so we can import xv_leak_tools
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..'))

from xv_leak_tools.helpers import exception_to_string
from xv_leak_tools.log import L
from xv_leak_tools.test_device.connector_helper import ConnectorHelper
from xv_leak_tools.test_device.device_discoverers.localhost_discoverer import LocalhostDiscoverer
from xv_leak_tools.test_execution.test_run_context import TestRunContext

def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    scriptlet_args = argv[1:]
    argv = argv[0:1]

    parser = argparse.ArgumentParser(description='Execute a scriptlet locally for testing')
    parser.add_argument(
        'scriptlet', help='Name of the scriptlet in the xv_leak_tools/scriplets folder')

    args = parser.parse_args(argv)

    L.configure({
        'trace': {
            'level': L.INFO,
        },
        'describe': {
            'file_format': None,
        },
        'report': {
            'file_format': None,
        },
    })

    try:
        L.info("Running scriptlet {} with args {}".format(args.scriptlet, scriptlet_args))

        context = TestRunContext({'output_directory': 'output'})
        localhost = LocalhostDiscoverer(context, []).discover_device({})
        helper = ConnectorHelper(localhost)
        L.info("scriptlet returned {}".format(helper.execute_scriptlet(
            'remote_mac_ver.py', scriptlet_args)))

    except BaseException as ex:
        L.info("scriptlet raised {}".format(ex))

    return 0

if __name__ == "__main__":
    # pylint: disable=broad-except
    try:
        sys.exit(main())
    except Exception as ex:
        sys.stderr.write("Unrecoverable error: {}\n".format(exception_to_string(ex)))
        sys.exit(-1)
