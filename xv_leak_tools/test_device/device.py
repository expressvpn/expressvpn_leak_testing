import ipaddress
import os

from abc import ABCMeta, abstractmethod

from xv_leak_tools.exception import XVEx
from xv_leak_tools.log import L

class Device(metaclass=ABCMeta):

    # pylint: disable=no-self-use

    def __init__(self, config, connector):
        self._config = config
        self._connector = connector
        self._components = {}
        self._check_config()

    def __getitem__(self, component_name):
        if component_name in self._components:
            return self._components[component_name]

        raise XVEx("Device {} has no component {}. Available components:\n{}".format(
            self.device_id(), component_name, "\n".join(self._components.keys())))

    def __setitem__(self, component_name, component):
        if component_name in self._components:
            raise XVEx("Can't add a component twice to a device: {}".format(component_name))
        self._components[component_name] = component

    def _check_config(self, extra_keys=None):
        required_keys = ['ips', 'device_id']
        if extra_keys is not None:
            required_keys += extra_keys
        for key in required_keys:
            if key not in self._config:
                raise XVEx("Device type {} requires the config key '{}'".format(
                    self.__class__.__name__, key))

    def setup(self):
        for _, component in list(self._components.items()):
            component.setup()

    def teardown(self):
        for _, component in list(self._components.items()):
            component.teardown()

    def config(self):
        return self._config

    @abstractmethod
    def os_name(self):
        pass

    @abstractmethod
    def os_version(self):
        pass

    def ips(self):
        return [ipaddress.ip_address(ip) for ip in self._config['ips']]

    # TODO: This was a bit of a bodge. Think about whether this is the right way to do things
    def update_ips(self, ips):
        L.debug("Updating device {} to use IPs {}".format(self.device_id(), ips))
        self._config['ips'] = ips
        self._connector.reset(ips)

    def device_id(self):
        return self._config['device_id']

    def connector(self):
        return self._connector

    def tools_root(self):
        '''Some types of devices will have this test suite checked out on them. Those devices should
        override this method and return the full path to the (git) root of the tools.'''
        return None

    # TODO: Doesn't make sense for (some) mobile devices. Consider either moving to derived class
    # or allowing this function to return None. N.B. Technically this does make some sense as every
    # device should have the concept of a non-root user which we want the tests to run as.
    def tools_user(self):
        # TODO: Desktop tests should be able to figure this out themselves rather than use a
        # config value
        return self._config['tools_user']

    # TODO: Might not make sense for (some) mobile devices. Consider either moving to derived class
    # or allowing this function to return None.
    def temp_directory(self):
        '''Get the location where temporary files should be written. This function doesn't guarantee
        that the folder exists. It is the user's responsibility to ensure it is created. We don't
        use the temp directory reported by functions like mktemp because we want any test output
        to be contained in a single location. Also, tests can run as root or another user so the
        directory reported by '''
        # Keep temp files in a subfolder of the test output directory
        return os.path.join(self.output_directory(), 'temp')

    # TODO: Might not make sense for (some) mobile devices. Consider either moving to derived class
    # or allowing this function to return None.
    def output_directory(self):
        return self._config['output_directory']

    # TODO: Unclear whether this should be abstract, should throw like this or should just warn
    # if unimplemented
    def kill_process(self, pid): # pylint: disable=unused-argument
        L.warning("TODO: kill_process not implemented for device {}".format(
            self.__class__.__name__))
        return None

    # TODO: Unclear whether this should be abstract, should throw like this or should just warn
    # if unimplemented
    def pgrep(self, _):
        L.warning("TODO: pgrep not implemented for device {}".format(self.__class__.__name__))
        return None

    # TODO: Unclear whether this should be abstract, should throw like this or should just warn
    # if unimplemented
    def command_line_for_pid(self, _):
        L.warning("TODO: command_line_for_pid not implemented for device {}".format(
            self.__class__.__name__))
        return None

    def report_info(self):
        info = "OS name: {}\n".format(self.os_name())
        info += "OS version: {}\n".format(self.os_version())
        return info

    def local_ips(self):
        L.warning("TODO: Local IP resolution not implemented for device {}".format(
            self.__class__.__name__))
        return []
