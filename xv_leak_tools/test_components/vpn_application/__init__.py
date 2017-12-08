from xv_leak_tools.test_components.vpn_application.vpn_application_builder import VPNApplicationBuilder

def register(factory):
    factory.register(VPNApplicationBuilder())
