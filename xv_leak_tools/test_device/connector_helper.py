import codecs
import os
import pickle
import tempfile
import hashlib

from xv_leak_tools.process import XVProcessException, XVEx
from xv_leak_tools.log import L

# TODO: I think we'll need a different implementation for Windows. Probably need to decide which
# one to construct based on the device.
class ConnectorHelper:

    def __init__(self, device):
        self._device = device
        # Create the temp dir first as checking virtual env relies on it
        self._create_temp_directory()
        self._check_virtual_env()

    @staticmethod
    def _sanitize_cmd(cmd):
        if not isinstance(cmd, list):
            raise XVEx(
                "Commands must be a list, passed command was a {}: {}".format(type(cmd), cmd))
        return [str(piece) for piece in cmd]

    def _check_virtual_env(self):
        '''Check that virtualenv was properly setup on the device. If we don't check and there's
        a problem then this can lead to cryptic errors from the helper function below. Better to
        catch this early on.'''
        try:
            # source doesn't error if the sourced fail is missing. This file "shouldn't" ever be
            # missing but let's check.
            self.check_command(['stat', '.pythonlocation'])
            self.check_command(['source', 'activate'])
        except XVProcessException as _:
            raise XVEx("Virtualenv doesn't appear to be setup properly for device '{}'".format(
                self._device.device_id()))

    def _create_temp_directory(self):
        # Note we can't use execute_scriptlet yet as that relies on the temp dir existing.
        L.debug("Ensuring temp directory {} exists".format(self._device.temp_directory()))
        cmd = ['mkdir', '-p', self._device.temp_directory()]
        ret, stdout, stderr = self._device.connector().execute(cmd)
        if ret:
            raise XVEx("Couldn't create temp directory: {}".format(
                XVProcessException(cmd, ret, stdout, stderr)))

        # if not is_root_user():
        #     return

        # cmd = ['chown', self._device.tools_user(), self._device.temp_directory()]
        # ret, stdout, stderr = self._device.connector().execute(cmd)
        # if ret:
        #     # Ignore the error, but expect failure
        #     L.warning("Couldn't chown temp directory {} back to user {}".format(
        #         self._device.temp_directory(), self._device.tools_user()))

    def check_command(self, cmd, root=False):
        cmd = ConnectorHelper._sanitize_cmd(cmd)
        ret, stdout, stderr = self.execute_command(cmd, root)
        if ret != 0:
            raise XVProcessException(cmd, ret, stdout, stderr)
        return stdout, stderr

    # TODO: We have the wrap exception stuff in scriptlets but won't have that here. I'm tempted
    # to say that commands always execute with python and are wrapped by subprocess scriptlet.
    def execute_command(self, cmd, root=False):
        cmd = ConnectorHelper._sanitize_cmd(cmd)
        # Escape spaces in paths. First part of command must be the executable.
        cmd[0] = "\"{}\"".format(cmd[0])

        script = '''\
cd {}
{}'''.format(self._device.tools_root(), ' '.join(cmd))

        L.debug("Executing shell command: {}".format(' '.join(cmd)))
        L.verbose("Using bash wrapper script:\n{}".format(script))
        return self.execute_script_remotely(script, root)

    def check_python(self, cmd, root=False):
        ret, stdout, stderr = self.execute_python(cmd, root)
        if ret != 0:
            raise XVProcessException(cmd, ret, stdout, stderr)
        return stdout, stderr

    # TODO: No MSDOS!
    # N.B. This always assumes that the PWD will be the leak tools root.
    def execute_python(self, cmd, root=False):
        cmd = ConnectorHelper._sanitize_cmd(cmd)
        # Escape spaces in paths. First part of command must (currently) be the script. Potentially
        # we might support flags to python I guess.
        cmd[0] = "\"{}\"".format(cmd[0])
        script = '''\
set -e
cd {}
source activate
set +e
python {}'''.format(self._device.tools_root(), ' '.join(cmd))

        L.debug("Executing python cmd: {}".format(' '.join(cmd)))
        L.verbose("Using python wrapper script:\n{}".format(script))
        return self.execute_script_remotely(script, root)

    # TODO: Maybe move this out into another file and make it run with anything that provides
    # execute_python
    def execute_scriptlet(self, scriptlet, args, root=False):
        '''A scriptlet is a specialised subprocess for executing python code. The code can only do
        one of two things: return a python object on success or throw an exception. A scriptlet
        must not do any outputting to stdout or stderr which it does not want to be un-pickled.
        The ideal use case is executing a python function remotely and getting its return value.
        '''
        cmd = [os.path.join(self._device.tools_root(), 'xv_leak_tools', 'scriptlets', scriptlet)]
        ret, stdout, stderr = self.execute_python(cmd + args, root)
        L.verbose("Scriptlet returned: ret: {}\nstdout: '{}'\nstderr: '{}'".format(
            ret, stdout, stderr))

        if ret != 0:
            raise pickle.loads(codecs.decode(stderr.encode(), "base64"))
        else:
            return pickle.loads(codecs.decode(stdout.encode(), "base64"))

    # TODO: This could like as a companion to the scriptlet rather than here.
    def remote_mkstemp(self, suffix=None, prefix=None, dir_=None, text=None):
        args = []
        if suffix:
            args += ["--suffix={}".format(suffix)]
        if prefix:
            args += ["--prefix={}".format(suffix)]
        if dir_:
            args += ["--dir={}".format(dir_)]
        if text:
            args += ["--text={}".format(text)]

        # Don't know what this can raise so let caller deal with it
        return self.execute_scriptlet('remote_mkstemp.py', args)

    def remote_mkdir(self, path, mode=None):
        args = [path]
        if mode:
            args += ["--mode={}".format(str(mode))]

        L.debug("Making remote directory: {}".format(path))
        self.execute_scriptlet('remote_mkdir.py', args)

    def remote_makedirs(self, path, mode=None):
        args = [path]
        if mode:
            args += ["--mode={}".format(str(mode))]

        L.debug("Making remote directories: {}".format(path))
        return self.execute_scriptlet('remote_makedirs.py', args)

    def execute_script_remotely(self, script_contents, root=False):
        # We generate a collision free (hopefully) name here as doing it on the remote device
        # means executing a script, so we get in a loop. We could do that by executing a
        # simpler script but this would likely mean it's not cross platform and/or we have
        # to worry about escape characters when we pass the script.
        hsh = hashlib.md5()
        hsh.update(script_contents.encode("utf-8"))
        remote_script_filename = "{}.sh".format(hsh.hexdigest())

        script_dst = os.path.join(self._device.temp_directory(), remote_script_filename)
        self.write_remote_file_from_contents(script_dst, script_contents)

        L.verbose("Executing remote script {}".format(script_dst))
        return self._device.connector().execute(['bash', script_dst], root=root)

    def write_remote_file_from_contents(self, path, contents):
        dst_filename = os.path.split(path)[1]
        hfile, tmpfile = tempfile.mkstemp("_{}".format(dst_filename), "xv_leak_test_")
        with os.fdopen(hfile, "w") as file_:
            file_.write(contents)

        L.verbose("Writing remote file {}".format(path))
        self._device.connector().push(tmpfile, path)
