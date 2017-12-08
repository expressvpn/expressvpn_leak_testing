from xv_leak_tools.factory import Builder
from xv_leak_tools.test_components.component import ComponentNotSupported
from xv_leak_tools.test_components.packet_capturer.packet_capturer import PacketCapturer

class PacketCaptureBuilder(Builder):

    @staticmethod
    def name():
        return 'packet_capturer'

    def build(self, device, config):
        if device.os_name() not in ['macos', 'linux', 'windows']:
            raise ComponentNotSupported("packet_capturer is not currently supported on {}".format(
                device.os_name()))

        return PacketCapturer(device, config)
