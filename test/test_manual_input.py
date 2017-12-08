import os
import sys
import unittest

from multiprocessing import Process, Queue

import mock

from xv_leak_tools.log import L
from xv_leak_tools.manual_input import allow_manual_input, disallow_manual_input
from xv_leak_tools.manual_input import message_and_await_string
from xv_leak_tools.manual_input import message_and_await_enter
# from xv_leak_tools.manual_input import message_and_await_yes_no

class AnyStringWithSubstring(str):
    def __eq__(self, other):
        return self in other

    def __repr__(self):
        return ".*{}.*".format(super().__str__())

class AnyStringWithSubstrings(list):
    def __eq__(self, other):
        for substr in self:
            if substr not in other:
                return False
        return True

    def __repr__(self):
        return ', '.join([".*{}.*".format(substr) for substr in self])

class TestManualInput(unittest.TestCase):

    def setUp(self):
        allow_manual_input()

    def tearDown(self):
        disallow_manual_input()

    @staticmethod
    def _call_method_in_subprocess(method, input_):
        queue = Queue()

        rpipe, wpipe = os.pipe()
        proc = Process(target=method, args=(queue, rpipe,))
        os.write(wpipe, input_.encode())
        proc.start()
        proc.join()

        os.close(wpipe)
        os.close(rpipe)

        return queue.get()

    def test_message_and_await_enter(self): # pylint: disable=no-self-use
        def call_message_and_await_enter(queue, fake_stdin):
            sys.stdin = os.fdopen(fake_stdin)
            with mock.patch('sys.stdout') as fake_stdout:
                L.configure()
                message_and_await_enter('Hello')

                fake_stdout.assert_has_calls([
                    mock.call.write(AnyStringWithSubstrings(['Hello', 'Press ENTER to continue'])),
                ])
            queue.put(None)

        TestManualInput._call_method_in_subprocess(call_message_and_await_enter, "\n")

    def test_message_and_await_string(self):
        def call_message_and_await_string(queue, fake_stdin):
            sys.stdin = os.fdopen(fake_stdin)
            with mock.patch('sys.stdout') as fake_stdout:
                L.configure()
                ret = message_and_await_string('Please give me some string data')

                fake_stdout.assert_has_calls([
                    mock.call.write(AnyStringWithSubstrings(['Please give me some string data'])),
                ])
            queue.put(ret)

        ret = TestManualInput._call_method_in_subprocess(call_message_and_await_string, "Bonza\n")
        self.assertEqual(ret, 'Bonza')

    # def test_message_and_await_yes_no(self):
    #     def call_message_and_await_yes_no(queue, fake_stdin):
    #         sys.stdin = os.fdopen(fake_stdin)
    #         with mock.patch('sys.stdout') as fake_stdout:
    #             L.configure()
    #             ret = message_and_await_yes_no('This is a yes or no question')

    #             fake_stdout.assert_has_calls([
    #                 mock.call.write(AnyStringWithSubstrings(['This is a yes or no question'])),
    #             ])
    #         queue.put(ret)

    #     for expected_in_out in [('y', True), ('n', False)]:
    #         ret = TestManualInput._call_method_in_subprocess(
    #             call_message_and_await_yes_no, expected_in_out[0])
    #         self.assertEqual(ret, expected_in_out[1])
