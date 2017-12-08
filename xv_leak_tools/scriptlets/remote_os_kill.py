#!/usr/bin/env python3
import argparse
import os
import sys

from wrap_scriptlet import wrap_scriptlet

def run():
    parser = argparse.ArgumentParser()
    parser.add_argument('pid')
    parser.add_argument('signal')
    args = parser.parse_args(sys.argv[1:])

    os.kill(int(args.pid), int(args.signal))
    return None

sys.exit(wrap_scriptlet(run))
