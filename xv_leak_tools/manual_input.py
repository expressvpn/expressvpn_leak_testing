import sys

# pylint: disable=global-statement

from xv_leak_tools.exception import XVEx
from xv_leak_tools.helpers import current_os, is_dos
from xv_leak_tools.log import L

_MANUAL_INPUT_ALLOWED = False

def _getch_unix():
    import tty
    import termios
    file_descriptor = sys.stdin.fileno()
    old_settings = termios.tcgetattr(file_descriptor)
    try:
        tty.setraw(sys.stdin.fileno())
        char = sys.stdin.read(1)
    finally:
        termios.tcsetattr(file_descriptor, termios.TCSADRAIN, old_settings)
    return char

def get_one_of(chars):
    while 1:
        char = getch()
        if ord(char) == 3:
            raise KeyboardInterrupt
        elif ord(char) == 4:
            raise EOFError
        elif char in chars:
            return char

def getch():
    if current_os() == 'windows' and is_dos():
        import msvcrt # pylint: disable=import-error
        return msvcrt.getch()
    return _getch_unix()

def check_manual_input_allowed():
    if not _MANUAL_INPUT_ALLOWED:
        raise XVEx('Manual input not allowed')

def allow_manual_input():
    global _MANUAL_INPUT_ALLOWED
    _MANUAL_INPUT_ALLOWED = True

def disallow_manual_input():
    global _MANUAL_INPUT_ALLOWED
    _MANUAL_INPUT_ALLOWED = False

# TIMEOUT = 60

# TODO Consider timeout and also get any key rather than entre
# TODO: Set some sort of global flag (Setting) so that if we try a manual instruction then the
# test immediately fails. Maybe the "Cant run on this machine" exception

def message_and_await_string(msg):
    check_manual_input_allowed()

    L.instruction(msg)
    sys.stdin.flush()
    return sys.stdin.readline().strip()

def message_and_await_enter(msg):
    check_manual_input_allowed()

    message_and_await_string("{}\nPress ENTER to continue...".format(msg))
    # L.warning("Manual interaction disabled!")

def message_and_await_yes_no(msg):
    check_manual_input_allowed()

    L.instruction(msg + ' (y/n)')
    char = get_one_of('yn')
    return True if char == 'y' else False
