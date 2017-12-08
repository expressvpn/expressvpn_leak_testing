from xv_leak_tools.factory import Builder
from xv_leak_tools.test_components.component import ComponentNotSupported
from xv_leak_tools.test_components.ip_tool.ip_tool_curl import IPToolCurl

class IPToolBuilder(Builder):

    @staticmethod
    def name():
        return 'ip_tool'

    def build(self, device, config):
        if device.os_name() in ['macos', 'windows', 'linux']:
            return IPToolCurl(device, config)
        raise ComponentNotSupported("ip_tool is not currently supported on {}".format(
            device.os_name()))
