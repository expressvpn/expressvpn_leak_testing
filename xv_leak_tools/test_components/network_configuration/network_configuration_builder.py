from xv_leak_tools.factory import Builder
from xv_leak_tools.test_components.network_configuration.network_configuration import NetworkConfiguration

class NetworkConfigurationBuilder(Builder):

    @staticmethod
    def name():
        return 'network_configuration'

    def build(self, device, config):
        return NetworkConfiguration(device, config)
