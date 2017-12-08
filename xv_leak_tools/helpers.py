import os
import sys
import time
import traceback

# Ensure this file has no major dependencies in the test suite, otherwise we can easily get circular
# references.
from xv_leak_tools.exception import XVEx

def unused(_):
    pass

def current_os():
    if sys.platform == 'linux' or sys.platform == 'linux2':
        return 'linux'
    elif sys.platform == 'darwin':
        return 'macos'
    elif sys.platform == 'win32' or sys.platform == 'cygwin':
        return 'windows'
    else:
        raise XVEx("Don't know which OS this is. sys.platform is {}".format(sys.platform))

def is_cygwin():
    return sys.platform == 'cygwin'

def is_dos():
    return current_os() == 'windows' and not is_cygwin()

def no_msdos():
    if is_dos():
        raise XVEx("Not supported on DOS")

def other_oses():
    other = ['linux', 'macos', 'windows']
    other.remove(current_os())
    return other

def is_root_user():
    if current_os() != 'windows':
        return os.geteuid() == 0
    else:
        # An ugly way of checking for admin on windows. It would be nicer to use
        # ctypes.windll.shell32.IsUserAnAdmin() but this isn't available on cygwin
        try:
            os.listdir(os.sep.join([os.environ.get('SYSTEMROOT', 'C:\\windows'), 'temp']))
            return True
        except PermissionError as ex:
            if 'Permission denied' in str(ex):
                return False
            # No idea what went wrong
            raise

def merge_two_dicts(into, merge_me):
    """Given two dicts, merge them into a new dict as a shallow copy."""
    new_dict = into.copy()
    new_dict.update(merge_me)
    return new_dict

# TODO: I've probably reinvented the wheel here
def exception_to_string(ex):
    return "Traceback (most recent call last):\n{}\nException: {}".format(
        ' '.join(traceback.format_tb(ex.__traceback__)), ex)

# I wouldn't be surprised if there's out of the box functionality to do this, but it's easy to write
# than search
class TimeUp:

    # pylint: disable=too-few-public-methods

    def __init__(self, seconds):
        self.seconds = seconds
        self.start = time.time()

    def __bool__(self):
        return time.time() - self.start >= self.seconds

    def time_left(self):
        return max(0, self.seconds - (time.time() - self.start))
