import os
import sys

from xv_leak_tools.exception import XVEx

# TODO: Think more about these helpers. python isn't doing a good job here of being cross
# platform!

def _cygwin_path_to_windows(path):
    if '/' not in path:
        return path
    prefix = ''
    if 'cygdrive' in path:
        index = path.rfind('cygdrive')
        after = path[index + len('cygdrive'):]
        if len(after) < 2:
            raise XVEx("Can't convert path '{}' to windows path".format(path))
        prefix = "{}:\\".format(after[1])
        path = after[2:]
    elif path[0] == '/':
        # TODO: Hardcoded drive and cygwin install path
        path = 'C:\\cygwin64' + path
    path = prefix + path.replace('/', '\\')
    # TODO: Fix this. Some logic somewhere is producing double slashes
    return path.replace('\\\\', '\\')

def _windows_path_to_cygwin(path):
    if '\\' not in path:
        return path
    prefix = ''
    if ':\\' in path:
        drive, path = path.split(':\\')
        prefix = "/cygdrive/{}/".format(drive.lower())

    return prefix + path.replace('\\', '/')

# TODO: Assumes no mixed slashes
def windows_path_split(path):
    if '\\' not in path:
        return os.path.split(path)
    path = path.replace('\\', '/')
    head, tail = os.path.split(path)
    return head.replace('/', '\\'), tail

def windows_safe_path(path):
    if sys.platform == 'cygwin':
        return _windows_path_to_cygwin(path)
    elif sys.platform == 'win32':
        if '/' in path:
            raise XVEx(
                "Running in DOS but path '{}' has a forward slash in it. Don't hardcode cygwin "
                "style paths".format(path))
        return path
    else:
        # Nothing to do for other OSes
        return path

def windows_real_path(path):
    if sys.platform == 'cygwin':
        return _cygwin_path_to_windows(path)
    elif sys.platform == 'win32':
        if '/' in path:
            raise XVEx(
                "Running in DOS but path '{}' has a forward slash in it. Don't hardcode cygwin "
                "style paths".format(path))
        return path
    else:
        # Nothing to do for other OSes
        return path

def makedirs_safe(path):
    try:
        os.makedirs(path)
    except OSError as ex:
        if 'File exists' not in str(ex):
            raise
