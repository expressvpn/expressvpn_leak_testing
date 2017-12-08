from xv_leak_tools.test_components.open_wrt.open_wrt_builder import OpenWRTBuilder

def register(factory):
    factory.register(OpenWRTBuilder())
