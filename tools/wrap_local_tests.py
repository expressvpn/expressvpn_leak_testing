#!/usr/bin/env python3

# TODO: Remove this once the sys.path.append is gone
# pylint: disable=wrong-import-position

import argparse
import json
import os
import sys

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..'))

from xv_leak_tools.log import L
from xv_leak_tools.exception import XVEx
from xv_leak_tools.object_parser import object_from_command_line

class LocalTestWrapper:

    # pylint: disable=too-few-public-methods

    @staticmethod
    def _validate_output_format(output_format):
        if output_format not in ['json']:
            raise XVEx("Unsupported output format: {}".format(output_format))

    @staticmethod
    def _output_filename(input_file, output_file, output_format):
        if output_file:
            return output_file

        return "{}.remote.{}".format(
            os.path.splitext(os.path.basename(input_file))[0], output_format)

    @staticmethod
    def _write_output_file(output_config, output_file, output_format):
        if output_format == "json":
            with open(output_file, 'w') as _file:
                json.dump(output_config, _file, indent=4)

        L.info("Wrote new config file {}".format(output_file))

    @staticmethod
    def _create_discovery_keys(device_id, os_name, os_version):
        discovery_keys = {}
        if device_id is not None:
            discovery_keys['device_id'] = device_id
        if os_name is not None:
            discovery_keys['os_name'] = os_name
        if os_version is not None:
            discovery_keys['os_version'] = os_version
        return discovery_keys

    @staticmethod
    def wrap(args):
        LocalTestWrapper._validate_output_format(args.format)
        test_configs = object_from_command_line(args.input_config, 'TESTS')

        discovery_keys = LocalTestWrapper._create_discovery_keys(
            args.device_id, args.os_name, args.os_version)

        output_configs = []

        for test in test_configs:
            output_configs.append({
                'name': 'TestCaseRemote',
                'devices' : [
                    {
                        'discovery_keys': discovery_keys,
                        'device_name': 'test_device',
                    }
                ],
                'parameters' : test,
            })

        output_file = LocalTestWrapper._output_filename(
            args.input_config, args.output_config, args.format)
        LocalTestWrapper._write_output_file(output_configs, output_file, args.format)

def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    parser = argparse.ArgumentParser(
        description='Wrap tests which can be run entirely on one machine for remote execution')
    parser.add_argument(
        'input_config', help='Either: a python file with a module level list attribute TESTS is '
        'list of tests; a json file whose top level element is an array of tests; or a json string '
        'parsable to a list of tests.')
    parser.add_argument('--device-id', default=None, help='Device to run the tests on.')
    parser.add_argument('--os-name', default=None, help='Device OS to run the tests on.')
    parser.add_argument('--os-version', default=None, help='Device OS version to run the tests on.')
    parser.add_argument(
        '--output_config', help='Root folder where all output for this test run will be written. '
        'You must create the folder first.')
    parser.add_argument(
        '--format', default='json', help='Output format of the generated config. Valid options '
        'are: json')
    args = parser.parse_args(argv)

    # TODO: I'm less and less happy with the logger now
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
    LocalTestWrapper.wrap(args)

if __name__ == "__main__":
    sys.exit(main())
