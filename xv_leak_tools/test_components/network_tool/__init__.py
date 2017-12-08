from xv_leak_tools.test_components.network_tool.network_tool_builder import NetworkToolBuilder

def register(factory):
    factory.register(NetworkToolBuilder())
