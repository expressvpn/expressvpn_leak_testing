#!/usr/bin/env python3
import argparse
import sys

import psutil

from wrap_scriptlet import wrap_scriptlet, debug_output

def run():
    parser = argparse.ArgumentParser()
    parser.add_argument('process_name')
    args = parser.parse_args(sys.argv[1:])

    pids = []
    for proc in psutil.process_iter():
        try:
            debug_output(proc.exe())
            if args.process_name in proc.exe():
                pids.append(proc.pid)
        except (psutil.ZombieProcess, psutil.AccessDenied, FileNotFoundError) as _:
            continue
    return pids

sys.exit(wrap_scriptlet(run))
