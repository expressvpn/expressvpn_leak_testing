#!/usr/bin/env python3

# pylint: disable=wrong-import-position

import argparse
import os
import re
import subprocess
import sys
import tempfile
import time
import ipaddress

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..'))

from xv_leak_tools import tools_user
from xv_leak_tools.exception import XVEx
from xv_leak_tools.helpers import exception_to_string, current_os
from xv_leak_tools.import_helpers import import_by_filename
from xv_leak_tools.log import L
from xv_leak_tools.object_parser import object_from_command_line
from xv_leak_tools.path import windows_safe_path, makedirs_safe
from xv_leak_tools.test_execution.test_run_context import TestRunContext
from xv_leak_tools.test_execution.test_runner import TestRunner
from xv_leak_tools.network.macos.pf_firewall import PFCtl

def punch_hole_in_firewall(ips):
    if current_os() == 'macos':
        pf = PFCtl()
        ip_list = '{ ' + ', '.join(ips) + ' }'
        pf.set_rules(["pass in quick from {} no state".format(ip_list),
                      "pass out quick to {} no state".format(ip_list)])
    elif current_os() == 'windows':
        L.warning("Ignoring option to open up firewall for {} on Windows".format(', '.join(ips)))
    else:
        raise XVEx('Editing the firewall is only supported for PF/macOS')

def filter_tests(tests, regex):
    filtered_tests = []
    L.info("Filtering tests with regex {}".format(regex))
    prog = re.compile(regex)

    for test in tests:
        if prog.match(test['name']):
            filtered_tests.append(test)

    L.info("Regex matched {}/{} tests".format(len(filtered_tests), len(tests)))
    return filtered_tests

def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    # Some of these command line args are also specified in the context. This is just for
    # convenience as certain of the arguments are changed often enough to warrant specifying them
    # on the command line.
    parser = argparse.ArgumentParser(
        description='Run a set of tests locally on the current machine. The exit code of this '
        '"command will be the number of tests which failed or, if an unexpected error occured, -1.')
    parser.add_argument(
        '-o', '--output-root', help='Root folder where all output for this test run will be '
        'written. Defaults to a system temp directory for the current user.')
    parser.add_argument(
        '-c', '--test-configs', default=[], nargs='+', help='Either: a python file with a module '
        'level list attribute TESTS is list of tests; a json file whose top level element is an '
        'array of tests; or a json string parsable to a list of tests.')
    parser.add_argument(
        '-d', '--test-devices', default=[], nargs='+', help='Either: a python file with a module '
        'level list attribute DEVICES is list of devices; a json file whose top level element is '
        'an array of devices; or a json string parsable to a list of tests.')
    parser.add_argument(
        '-r', '--run-directory', default=None, help='A unique subdirectory of the output_root '
        'where results for this specific run will go. If not specified then a unique one will be '
        "generated based on the run timestamp. The directory will be created if it doesn't exist")
    parser.add_argument(
        '-m', '--allow-manual', default=None, action='store_true',
        help='Allow manual tests. If this is not specified then any test which requires manual '
        'interaction will fail')
    parser.add_argument(
        '-s', '--stop-on-fail', default=None, action='store_true',
        help='If specified, the test run will stop as soon as the first test fails.')
    parser.add_argument(
        '-t', '--test-regex', default=None, help='If specified, only run tests whose test class '
        'name matches the passed regex.')
    parser.add_argument(
        '-x', '--context', default='default_context.py', help='If specified, only run tests whose '
        'test class name matches the passed regex.')
    parser.add_argument(
        '-l', '--log-level', default=None, help='Log level. Valid values ["ERROR", "WARNING", '
        '"INFO", "DEBUG", "VERBOSE"].')
    parser.add_argument(
        '-2', '--v2', default=False, action='store_true', help='DEPRECATED: Does nothing')
    parser.add_argument(
        '-f', '--firewall_exemption', default=None, metavar="IP", nargs='+',
        help='Punch a hole in the firewall for the given IP address.')
    parser.add_argument(
        '-p', '--pidfile', default=None, metavar='PATH_TO_PIDFILE', nargs=1,
        help='File to write the PID to.')
    args = parser.parse_args(argv)

    args.log_level = args.log_level.upper() if args.log_level else None
    # We'll reconfigure in a second but lets get logging going asap!
    inital_log_level = args.log_level if args.log_level else "INFO"
    TestRunner.configure_logger(level=inital_log_level)

    if args.pidfile:
        pid = os.getpid()
        path = os.path.abspath(args.pidfile.pop())
        L.debug("Writing PID {} to {}".format(pid, path))
        with open(path, 'w') as pidfile:
            pidfile.write(str(pid))

    if args.output_root is None:
        if current_os() == "windows":
            args.output_root = tempfile.mkdtemp()
        else:
            # Don't make the folder as root else we'll get perms issues. This also ensures we use
            # the user's temp directory not root's temp directory.
            args.output_root = subprocess.check_output(
                ['sudo', '-u', tools_user()[1], 'mktemp', '-d']).decode().strip()
        L.warning("You didn't specify an output folder. Using: {}".format(args.output_root))

    args.output_root = windows_safe_path(args.output_root)

    if not os.path.exists(args.output_root):
        makedirs_safe(args.output_root)

    if args.run_directory is None:
        args.run_directory = "Run_{}".format(time.time())

    # Just add output_directory to the args object as it makes life simpler.
    args.output_directory = os.path.join(args.output_root, args.run_directory)
    makedirs_safe(args.output_directory)

    if args.firewall_exemption:
        ips = [ipaddress.ip_network(ip).exploded for ip in args.firewall_exemption]
        L.info("Punching hole for {}".format(', '.join(ips)))
        punch_hole_in_firewall(ips)

    context_dict = import_by_filename(args.context).CONTEXT
    cmd_line_overrides = [
        'run_directory',
        'output_directory',
        'allow_manual',
        'stop_on_fail',
        'log_level',
    ]

    for override in cmd_line_overrides:
        value = getattr(args, override)
        if value is not None:
            context_dict[override] = value

    # Log level might need updating based on config
    TestRunner.configure_logger(args.output_directory, level=getattr(L, context_dict['log_level']))

    test_configs = []
    for test_config_file in args.test_configs:
        test_configs += object_from_command_line(test_config_file, 'TESTS')

    test_devices = []
    for test_device_file in args.test_devices:
        test_devices += object_from_command_line(test_device_file, 'DEVICES')

    if args.test_regex:
        test_configs = filter_tests(test_configs, args.test_regex)

    # This call shouldn't throw. If it does then we need to tweak the TestRunner.
    if args.v2:
        L.warning(
            "Argument -2 is DEPRECATED and will be ignored. Test runner v2 is the default now")
    return TestRunner(TestRunContext(context_dict), test_devices, test_configs).run()

if __name__ == "__main__":
    # pylint: disable=broad-except
    try:
        sys.exit(main())
    except Exception as ex:
        L.error("Unrecoverable error: {}\n".format(exception_to_string(ex)))
        sys.exit(-1)
