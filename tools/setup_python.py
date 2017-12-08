#!/usr/bin/env python

# pylint: disable=wrong-import-position

import os
import subprocess
import sys
import tempfile

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..'))

from xv_leak_tools.helpers import current_os

if len(sys.argv) != 2:
    sys.stderr.write("USAGE: setup_python.py virtualenv_location\n")
    sys.exit(1)

def bin_path():
    if current_os() == 'macos':
        return '/usr/local/bin/'
    return '/usr/bin/'

def install_python_if_not_present(location):
    if os.path.exists(os.path.join(location, 'bin', 'activate')):
        print("Virtualenv already setup in {}".format(location))
        return

    print("Creating virtualenv")
    cmd = [
        os.path.join(bin_path(), 'virtualenv'),
        '-p',
        os.path.join(bin_path(), 'python3'),
        location
    ]
    print("Executing: {}".format(" ".join(cmd)))
    subprocess.check_output(cmd)
    write_pythonlocation(location)

def install_pip_packages():
    if sys.platform == 'linux' or sys.platform == 'linux2':
        requirements = 'requirements_linux.txt'
    elif sys.platform == 'darwin':
        requirements = 'requirements_macos.txt'
    elif sys.platform == 'cygwin':
        requirements = 'requirements_windows.txt'
    else:
        raise Exception("Unsupported system: {}".format(sys.platform))

    print("Installing pip packages using {}".format(requirements))

    script = '''\
source activate
pip3 install -r {}
'''.format(requirements)

    _file, script_file = tempfile.mkstemp()
    with os.fdopen(_file, 'w') as _file:
        _file.write(script)

    print("Wrote temp file to {}".format(script_file))
    try:
        for line in subprocess.check_output(['bash', script_file]).splitlines():
            print(line.decode())
    except subprocess.CalledProcessError as ex:
        print("FAILED: {}".format(ex))
        sys.exit(1)

def write_pythonlocation(location):
    with open('.pythonlocation', 'w') as _file:
        _file.write(location)

LOCATION = sys.argv[1]
print("Setting up python in {}".format(LOCATION))

install_python_if_not_present(LOCATION)
# Write the python location first as the pip step relies on it
write_pythonlocation(LOCATION)
# We always install pip packages so that updates from the repo get picked up. On the build machines
# this is very useful. It's cheap to pip install if everything is already installed.
install_pip_packages()
