import re

from xv_leak_tools.exception import XVEx
from xv_leak_tools.test_components.route.route import Route
from xv_leak_tools.test_device.connector_helper import ConnectorHelper

class LinuxRoute(Route):

    PROG_ROW = re.compile(
        r"^([^\s]+)\s+([^\s]+)\s+([^\s]+)\s+([^\s]+)\s+([^\s]+)\s+([^\s]+)\s*([^\s]*)$")

    def __init__(self, device, config):
        super().__init__(device, config)
        self._connector_helper = ConnectorHelper(self._device)

    def get_v4_routes(self):
        raise XVEx("TODO: get_v4_routes not implemented on linux")
