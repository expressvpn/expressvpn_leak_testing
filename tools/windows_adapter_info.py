#!/usr/bin/env python3

# TODO: Remove this once the sys.path.append is gone
# pylint: disable=wrong-import-position

import os
import sys

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..'))

from xv_leak_tools.network.windows.windows_network import WindowsNetwork

for adapter in WindowsNetwork.adapters_in_priority_order():
    print(adapter.pretty_string())
    # print(adapter.all_string())
    print("-" * 80)
