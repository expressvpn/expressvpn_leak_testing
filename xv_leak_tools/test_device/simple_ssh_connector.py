import errno
import os
import socket
import stat
import subprocess
import tempfile

import netifaces
import paramiko

from xv_leak_tools.exception import XVEx
from xv_leak_tools.helpers import current_os
from xv_leak_tools.log import L
from xv_leak_tools.path import makedirs_safe
from xv_leak_tools.test_device.connector import Connector

class SimpleSSHConnector(Connector):

    # pylint: disable=too-few-public-methods,too-many-arguments

    # TODO: Account password shouldn't be needed. Paramiko is either or.
    def __init__(self, ips, username, account_password=None, ssh_key=None, ssh_password=None):
        self._ips = ips
        self._username = username.encode('utf-8') if username else None
        self._account_password = account_password
        self._ssh_key = ssh_key
        self._ssh_password = ssh_password.encode('utf-8') if ssh_password else None
        self._ssh_client = None
        self._sftp_client = None
        self._routes_to_remote = []

    def __del__(self):
        self._remove_routes()

    def _ensure_connected(self):
        if self._ssh_client:
            return

        self._ssh_connect()

    def _remove_routes(self):
        for route in self._routes_to_remote:
            subprocess.check_output(['route', 'delete'] + route)
        self._routes_to_remote = []

    def _create_route_to_ip(self, ip):
        default_gateway = netifaces.gateways()['default'][netifaces.AF_INET][0]
        L.debug("Adding route to ip: {} -> {}".format(ip, default_gateway))
        if current_os() == 'windows':
            raise XVEx("TODO: Implement route on windows")
        else:
            route = [ip, default_gateway]
            subprocess.check_output(['route', 'add'] + route)
            self._routes_to_remote.append(route)

    def _ssh_connect(self):
        connect_errors = ""
        for ip in self._ips:
            self._create_route_to_ip(ip)
            connect_dict = {
                'hostname': ip,
                'username': self._username,
                'password': self._ssh_password,
                'key_filename': self._ssh_key,
                'timeout': 5,
            }

            L.debug("Connecting SSH with args {}".format(connect_dict))

            self._ssh_client = paramiko.SSHClient()
            self._ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            try:
                self._ssh_client.connect(**connect_dict)
                self._sftp_client = self._ssh_client.open_sftp()
                return
            except (paramiko.ssh_exception.NoValidConnectionsError, socket.timeout) as ex:
                connect_errors += "Couldn't connect to host via SSH connection at {}: {}\n".format(
                    ip, ex)
        raise XVEx("Couldn't connect to host:\n{}".format(connect_errors))

    def _ssh_disconnect(self):
        L.debug("Disconnecting SSH")

        if self._sftp_client:
            self._sftp_client.close()
            self._sftp_client = None
        if self._ssh_client:
            self._ssh_client.close()
            self._ssh_client = None

        self._remove_routes()

    def _is_file(self, filename):
        return not self._is_dir(filename)

    def _is_dir(self, filename):
        return stat.S_ISDIR(self._sftp_client.stat(filename).st_mode)

    # TODO: Move to helper?
    def _sftp_walk(self, root):
        files = []
        directories = []
        for file_ in self._sftp_client.listdir_attr(root):
            if stat.S_ISDIR(file_.st_mode):
                directories.append(file_.filename)
            else:
                files.append(file_.filename)

        yield root, directories, files

        for directory in directories:
            sub_dir = os.path.join(root, directory)
            for ret in self._sftp_walk(sub_dir):
                yield ret

    def _pull_file_append(self, src, dst):
        L.verbose("Appending file from remote machine to local file: {} <- {}".format(dst, src))

        hfile, temp_path = tempfile.mkstemp(
            suffix="_{}".format(os.path.split(src)[1]), prefix='xv_leak_test_')

        os.close(hfile)
        self._sftp_client.get(src, temp_path)

        with open(temp_path) as f_src:
            contents = f_src.read()
            with open(dst, "a") as f_dst:
                f_dst.write(contents)

    def _pull_dir(self, src, dst, append_duplicate=True):
        L.debug("Pulling directory from remote machine: {} <- {}".format(dst, src))
        self._sftp_client.chdir(src)
        makedirs_safe(dst)

        for root, _, files in self._sftp_walk(src):
            subdir = os.path.join(dst, os.path.relpath(root, src))
            L.verbose("Creating subfolder {}".format(subdir))
            makedirs_safe(subdir)
            for file_ in files:
                src_file = os.path.join(root, file_).replace('\\', '/')
                dst_file = os.path.join(subdir, file_).replace('\\', '/')
                if append_duplicate and os.path.exists(dst_file):
                    self._pull_file_append(src_file, dst_file)
                else:
                    L.verbose("Pulling file from remote machine: {} <- {}".format(dst, src))
                    self._sftp_client.get(src_file, dst_file)

    def _pull_file(self, src, dst):
        L.debug("Pulling file from remote machine: {} <- {}".format(dst, src))
        self._sftp_client.get(src, dst)

    def reset(self, ips):
        self._ssh_disconnect()
        self._ips = ips

    def execute(self, cmd, root=False):
        self._ensure_connected()

        if root and self._username.decode() != 'root':
            cmd = ['sudo', '-n'] + cmd

        L.verbose("SimpleSSHConnector: Executing remote command: '{}'".format(cmd))

        chan = self._ssh_client.get_transport().open_session()
        chan.settimeout(2)
        # TODO: This will block if stdin on the remote machine blocks. Can't ctrl-c. Consider a
        # custom wrapper with select and timeout
        chan.exec_command(' '.join(cmd))
        bufsize = -1
        # stdin = chan.makefile('wb', bufsize)
        stdout = chan.makefile('r', bufsize)
        stderr = chan.makefile_stderr('r', bufsize)

        retcode = chan.recv_exit_status()
        # paramiko splits output into a list AND keeps the newline. So joining like this puts it
        # back to how we'd "normally" expect output.
        return retcode, ''.join(stdout), ''.join(stderr)

    def push(self, src, dst):
        self._ensure_connected()

        # TODO: Can this do dirs?
        L.verbose("Pushing file/directory to remote machine: {} -> {}".format(src, dst))
        self._sftp_client.put(src, dst)

    def pull(self, src, dst):
        self._ensure_connected()

        try:
            if self._is_file(src):
                self._pull_file(src, dst)
            else:
                self._pull_dir(src, dst)
        except IOError as ex:
            if ex.errno == errno.ENOENT:
                raise XVEx("Path '{}' does not exist on remote device".format(src))
            # No idea what went wrong, just re-raise the existing exception
            raise
