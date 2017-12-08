#!/usr/bin/env python3
import argparse
import os
import sys
import tempfile

from wrap_scriptlet import wrap_scriptlet

def run():
    parser = argparse.ArgumentParser()
    parser.add_argument('--suffix')
    parser.add_argument('--prefix')
    parser.add_argument('--dir')
    args = parser.parse_args(sys.argv[1:])

    filehandle, filename = tempfile.mkstemp(suffix=args.suffix, prefix=args.prefix, dir=args.dir)
    os.close(filehandle)
    return filename

sys.exit(wrap_scriptlet(run))
