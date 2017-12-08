from xv_leak_tools.test_components.packet_capturer.packet_capturer_builder import PacketCaptureBuilder

def register(factory):
    factory.register(PacketCaptureBuilder())
