#!/usr/bin/env python3
import platform
import sys

from wrap_scriptlet import wrap_scriptlet

def run():
    return platform.mac_ver()

sys.exit(wrap_scriptlet(run))
