from xv_leak_tools import tools_user, tools_root
from xv_leak_tools.exception import XVEx
from xv_leak_tools.helpers import current_os
from xv_leak_tools.log import L
from xv_leak_tools.test_device.device_discoverers.device_discoverer import DeviceDiscoverer
from xv_leak_tools.test_device.local_shell_connector import LocalShellConnector
from xv_leak_tools.test_device.create_device import create_device
from xv_leak_tools.test_device.windows_local_shell_connector import WindowsLocalShellConnector

class LocalhostDiscoverer(DeviceDiscoverer):

    def __init__(self, context, device_inventory):
        super().__init__(context, device_inventory)
        if len(self._device_inventory) >= 2:
            raise XVEx('localhost has been specified more than once in the device inventory')

        if len(self._device_inventory) == 1:
            self._localhost_config = self._device_inventory[0]
        else:
            self._localhost_config = {}

        self._set_config_defaults()

    @staticmethod
    def discovery_type():
        return 'localhost'

    def _set_config_defaults(self):
        self._localhost_config['device_id'] = 'localhost'
        self._localhost_config['ips'] = ['127.0.0.1']
        self._localhost_config['output_directory'] = self._context['output_directory']
        self._localhost_config['tools_root'] = tools_root()
        self._localhost_config['tools_user'] = tools_user()[1]

    def discover_device(self, discovery_keys):
        if 'device_id' not in discovery_keys or discovery_keys['device_id'] != 'localhost':
            return None

        if len(discovery_keys) != 1:
            L.warning(
                "Only the 'device_id' discovery key is valid for discovering localhost. The others "
                "will be ignored: {}".format(discovery_keys))

        if current_os() == 'windows':
            connector = WindowsLocalShellConnector()
        else:
            connector = LocalShellConnector()
        return create_device(current_os(), self._localhost_config, connector)
