#!/usr/bin/env python3

# TODO: Remove this once the sys.path.append is gone
# pylint: disable=wrong-import-position

import argparse
import json
import os
import sys

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..'))

from xv_leak_tools.helpers import exception_to_string
from xv_leak_tools.object_parser import object_from_command_line

def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    # Some of these command line args are also specified in the context. This is just for
    # convenience as certain of the arguments are changed often enough to warrant specifying them
    # on the command line.
    parser = argparse.ArgumentParser(
        description='')
    parser.add_argument(
        'template', help='')
    args = parser.parse_args(argv)

    test_configs = object_from_command_line(args.template, 'TESTS')
    print(len(test_configs))
    output_file = 'tests.json'
    with open(output_file, 'w') as _file:
        json.dump(test_configs, _file, indent=4)
    print("Wrote json file: {}".format(output_file))

if __name__ == "__main__":
    # pylint: disable=broad-except
    try:
        sys.exit(main())
    except Exception as ex:
        sys.stderr.write("Unrecoverable error: {}\n".format(exception_to_string(ex)))
        sys.exit(-1)
