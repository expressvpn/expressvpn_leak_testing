from xv_leak_tools.test_components.firewall.firewall_builder import FirewallBuilder

def register(factory):
    factory.register(FirewallBuilder())
