from xv_leak_tools.test_device.device_discoverers.localhost_discoverer import LocalhostDiscoverer
from xv_leak_tools.test_device.device_discoverers.static_discoverer import StaticDeviceDiscoverer
from xv_leak_tools.test_device.device_discoverers.vmware_discoverer import VMWareDeviceDiscoverer
from xv_leak_tools.exception import XVEx

class DeviceDiscovery:

    def __init__(self, context, inventory):
        # No need for anything clever here yet. We only have 3 ways of discovering devices
        # currently. Let's just add the discoverers manually.
        self._discoverers = []
        self._discoverers.append(LocalhostDiscoverer(context, inventory))
        self._discoverers.append(StaticDeviceDiscoverer(context, inventory))
        self._discoverers.append(VMWareDeviceDiscoverer(context, inventory))

    def discover_device(self, discovery_keys):
        for discoverer in self._discoverers:
            device = discoverer.discover_device(discovery_keys)
            if device is not None:
                return device
        raise XVEx("Couldn't discover device using keys: {}".format(discovery_keys))

    def release_devices(self):
        for discoverer in self._discoverers:
            discoverer.release_devices()

    def cleanup(self):
        for discoverer in self._discoverers:
            discoverer.cleanup()
