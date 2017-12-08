import sys
import unittest

import mock
from parameterized import parameterized

from xv_leak_tools.helpers import current_os
from xv_leak_tools.helpers import merge_two_dicts
from xv_leak_tools.helpers import other_oses

class TestOSHelpers(unittest.TestCase):

    def test_current_os(self):
        for plat in ['linux', 'linux2']:
            with mock.patch.object(sys, 'platform', plat):
                self.assertEqual(current_os(), 'linux')

        with mock.patch.object(sys, 'platform', 'darwin'):
            self.assertEqual(current_os(), 'macos')

        for plat in ['win32', 'cygwin']:
            with mock.patch.object(sys, 'platform', plat):
                self.assertEqual(current_os(), 'windows')

        with mock.patch.object(sys, 'platform', 'unknown'):
            with self.assertRaises(Exception):
                current_os()

    def test_other_oses(self):
        plat_and_others = [
            ('linux', ['windows', 'macos']),
            ('darwin', ['windows', 'linux']),
            ('win32', ['linux', 'macos']),
        ]

        for plat, others in plat_and_others:
            with mock.patch.object(sys, 'platform', plat):
                self.assertEqual(set(others), set(other_oses()))

class TestMergeTwoDicts(unittest.TestCase):

    DICT1 = {'a': 1, 'b': 2, 'c': 3}
    DICT2 = {'d': 4, 'e': 5, 'f': 6}
    DICT3 = {'a': 4, 'b': 5, 'c': 6}
    DICT4 = {'c': 4, 'd': 5, 'e': 6}
    MERGED1_2 = {'a': 1, 'b': 2, 'c': 3, 'd': 4, 'e': 5, 'f': 6}
    MERGED1_4 = {'a': 1, 'b': 2, 'c': 4, 'd': 5, 'e': 6}

    @parameterized.expand([
        (DICT1, DICT2, MERGED1_2),
        (DICT1, DICT3, DICT3),
        ({}, DICT1, DICT1),
        (DICT1, {}, DICT1),
        (DICT1, DICT4, MERGED1_4),
    ])

    def test_merge_two_dicts(self, dict1, dict2, merged):
        self.assertEqual(merge_two_dicts(dict1, dict2), merged)

if __name__ == '__main__':
    unittest.main()
