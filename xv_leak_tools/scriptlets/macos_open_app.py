#!/usr/bin/env python3
import argparse
import subprocess
import sys
import time

from wrap_scriptlet import wrap_scriptlet

def run():
    parser = argparse.ArgumentParser()
    parser.add_argument('bundle_path')
    args = parser.parse_args(sys.argv[1:])

    subprocess.call(['open', args.bundle_path])
    # Pause briefly to allow app to open
    # TODO: not ideal
    time.sleep(1)
    return 0

sys.exit(wrap_scriptlet(run))
