import filecmp
import os
import shutil
import tempfile
import unittest

from xv_leak_tools.test_device.local_shell_connector import LocalShellConnector

class TestLocalShellConnector(unittest.TestCase):

    def setUp(self):
        self.connector = LocalShellConnector()
        self.here = os.path.dirname(os.path.realpath(__file__))
        self.output_folder = tempfile.mkdtemp('_test_local_shell_connector', 'xv_leak_test_')
        # print("Using dir {}\n".format(self.output_folder))

    def tearDown(self):
        shutil.rmtree(self.output_folder)

    def test_execute(self):
        # TODO: Lots to test here. Root, not root etc.
        pass

    # TODO: Test push with root. N.B. I'm not sure root logic is needed for push

    def test_push_file_src_missing(self):
        src = os.path.join('no', 'way', 'i', 'exist')
        dst = self.output_folder
        def wrapper():
            self.connector.push(src, dst)
        self.assertRaises(Exception, wrapper)

    def test_push_file_dst_folder_only_specified(self):
        src = os.path.join(self.here, 'folder_to_push_pull', 'top_level_file.txt')
        dst = self.output_folder
        self.connector.push(src, dst)
        self.assertTrue(os.path.exists(os.path.join(self.output_folder, 'top_level_file.txt')))
        self.assertTrue(filecmp.cmp(src, os.path.join(self.output_folder, 'top_level_file.txt')))

    def test_push_file_dst_filename_specified(self):
        src = os.path.join(self.here, 'folder_to_push_pull', 'top_level_file.txt')
        dst = os.path.join(self.output_folder, 'some_filename.txt')
        self.connector.push(src, dst)
        self.assertTrue(os.path.exists(dst))
        self.assertTrue(filecmp.cmp(src, dst))

    def test_push_folder(self):
        src = os.path.join(self.here, 'folder_to_push_pull')
        dst = self.output_folder
        self.connector.push(src, dst)
        self.assertTrue(os.path.isdir(os.path.join(dst, 'folder_to_push_pull')))

        dcmp = filecmp.dircmp(src, os.path.join(dst, 'folder_to_push_pull'), ignore=[])
        self.assertEqual(0, len(dcmp.left_only))
        self.assertEqual(0, len(dcmp.right_only))
        self.assertEqual(0, len(dcmp.diff_files))
        self.assertEqual(0, len(dcmp.funny_files))

    def test_pull_file_src_missing(self):
        pass

    def test_pull_file_dst_folder_only_specified(self):
        pass

    def test_pull_file_dst_filename_specified(self):
        pass

    def test_pull_folder(self):
        pass
