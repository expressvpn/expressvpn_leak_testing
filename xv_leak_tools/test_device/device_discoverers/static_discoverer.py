import os

from xv_leak_tools.exception import XVEx
from xv_leak_tools.log import L
from xv_leak_tools.test_device.create_device import create_device
from xv_leak_tools.test_device.device_discoverers.device_discoverer import DeviceDiscoverer
from xv_leak_tools.test_device.simple_ssh_connector import SimpleSSHConnector
from xv_leak_tools.test_device.adb_connector import ADBConnector
from xv_leak_tools.test_device.dummy_connector import DummyConnector

class StaticDeviceDiscoverer(DeviceDiscoverer):

    @staticmethod
    def discovery_type():
        return 'static'

    def discover_device(self, discovery_keys):
        L.debug('Looking for device with keys {}'.format(discovery_keys))

        device = self._inventory_item_for_discovery_keys(discovery_keys)
        if device is None:
            return None

        if 'output_root' not in device:
            raise XVEx("Device config didn't specify 'output_root': {}".format(device))

        device['output_directory'] = os.path.join(
            device['output_root'], self._context['run_directory'])

        # TODO: Look into refactoring this.
        if 'dummy' in device and device['dummy']:
            connector = DummyConnector()
        elif 'adb_id' in device and device['adb_id']:
            connector = ADBConnector(device['adb_id'])
        else:
            connector = SimpleSSHConnector(
                ips=device['ips'],
                username=device['username'],
                account_password=device.get('account_password', None),
                ssh_key=device.get('ssh_key', None),
                ssh_password=device.get('ssh_password', None)
            )

        return create_device(device['os_name'], device, connector)
