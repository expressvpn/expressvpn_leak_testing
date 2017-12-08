from xv_leak_tools.test_components.dns_tool.dns_tool_builder import DNSToolBuilder

def register(factory):
    factory.register(DNSToolBuilder())
