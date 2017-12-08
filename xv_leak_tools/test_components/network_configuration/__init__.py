from xv_leak_tools.test_components.network_configuration.network_configuration_builder import NetworkConfigurationBuilder

def register(factory):
    factory.register(NetworkConfigurationBuilder())
