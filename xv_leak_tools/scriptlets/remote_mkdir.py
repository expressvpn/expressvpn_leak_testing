#!/usr/bin/env python3
import argparse
import os
import sys

from wrap_scriptlet import wrap_scriptlet

class ActionStringToOctal(argparse.Action): # pylint: disable=too-few-public-methods
    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, int(values, 8))

def run():
    parser = argparse.ArgumentParser()
    parser.add_argument('path')
    parser.add_argument('--mode', action=ActionStringToOctal)
    args = parser.parse_args(sys.argv[1:])

    if args.mode:
        os.mkdir(args.path, args.mode)
    else:
        os.mkdir(args.path)
    return None

sys.exit(wrap_scriptlet(run))
