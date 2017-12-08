import copy
from abc import ABCMeta, abstractmethod

from xv_leak_tools.exception import XVEx

class DeviceDiscoverer(metaclass=ABCMeta):

    def __init__(self, context, device_inventory):
        self._context = context
        self._device_inventory = []
        for device in device_inventory:
            if device['discovery_type'] != self.__class__.discovery_type():
                continue
            self._device_inventory.append(device)

    @staticmethod
    def _matches_keys(device, discovery_keys):
        for key, value in list(discovery_keys.items()):
            if key not in device or device[key] != value:
                return False
        return True

    def _inventory_item_for_discovery_keys(self, discovery_keys):
        match = None
        for device in self._device_inventory:
            if not DeviceDiscoverer._matches_keys(device, discovery_keys):
                continue
            if match is not None:
                raise XVEx(
                    "Found two devices in the inventory matching the keys:\n{}\n{}".format(
                        match, device))
            match = device

        if match is None:
            return None

        return copy.deepcopy(match)

    @abstractmethod
    def discover_device(self, discovery_keys):
        pass

    def release_devices(self):
        pass

    def cleanup(self):
        pass
