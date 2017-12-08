#!/usr/bin/env python3
import argparse
import sys

import psutil

from wrap_scriptlet import wrap_scriptlet

def run():
    parser = argparse.ArgumentParser()
    parser.add_argument('pid')
    args = parser.parse_args(sys.argv[1:])

    process = psutil.Process(int(args.pid))
    return process.cmdline()

sys.exit(wrap_scriptlet(run))
