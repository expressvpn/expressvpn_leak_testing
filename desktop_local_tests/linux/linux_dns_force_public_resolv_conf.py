import os
from desktop_local_tests.disrupter import Disrupter
from xv_leak_tools.exception import XVEx
from xv_leak_tools.log import L

class LinuxDNSForcePublicResolvConfDisrupter(Disrupter):

    def __init__(self, device, parameters):
        super().__init__(device, parameters)
        self._restrict_parameters(must_disrupt=True, must_restore=False, must_wait=False)
        self._resolv_conf_path = "/etc/resolv.conf"
        self._resolv_conf_target_path = None
        self._temp_resolv_conf_path = os.path.join(device.temp_directory(), "resolv.conf")

    def disrupt(self):
        L.describe('Set the DNS servers in resolv.conf to public DNS servers')

        temp_resolv_conf = open(self._temp_resolv_conf_path, "w")
        # TODO: make configurable?
        dns_servers = ['37.235.1.174', '37.235.1.177']
        for nameserver in dns_servers:
            temp_resolv_conf.write("nameserver {}\n".format(nameserver))
        temp_resolv_conf.close()

        if os.path.islink(self._resolv_conf_path) and os.path.exists(self._resolv_conf_path):
            self._resolv_conf_target_path = os.readlink(self._resolv_conf_path)
            os.remove(self._resolv_conf_path)
            os.symlink(self._temp_resolv_conf_path, self._resolv_conf_path)
            os.sync()
        else:
            raise XVEx("Can't replace resolv.conf; not a symlink")

    def _restore_dns_servers(self):
        os.remove(self._resolv_conf_path)
        os.symlink(self._resolv_conf_target_path, self._resolv_conf_path)
        os.sync()

    def teardown(self):
        self._restore_dns_servers()
        super().teardown()
