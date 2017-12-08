#!/usr/bin/env python3

# TODO: Remove this once the sys.path.append is gone
# pylint: disable=wrong-import-position

import os
import sys

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..'))

from xv_leak_tools.test_documentation.test_docstring_reader import TestDocstringRead

DOCS = TestDocstringRead([
    'xv_leak_tools.test_framework',
    'desktop_local_tests',
]).docs()

NO_DOCS = []

for test_class, doc in list(DOCS.items()):
    if doc['doc'] is None:
        NO_DOCS.append(test_class)
    else:
        print(test_class)
        print('-' * len(test_class))
        print(doc['doc'])
        print()

if len(NO_DOCS) != 0:
    WARN_STRING = 'Warning the following tests have no documentation'
    print("\n{}".format(WARN_STRING))
    print('-' * len(WARN_STRING))
    print()
    for test_class in NO_DOCS:
        print(test_class)
