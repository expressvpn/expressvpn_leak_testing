from xv_leak_tools.test_components.ip_responder.ip_responder_builder import IPResponderBuilder

def register(factory):
    factory.register(IPResponderBuilder())
