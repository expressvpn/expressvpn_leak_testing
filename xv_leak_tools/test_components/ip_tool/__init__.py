from xv_leak_tools.test_components.ip_tool.ip_tool_builder import IPToolBuilder

def register(factory):
    factory.register(IPToolBuilder())
