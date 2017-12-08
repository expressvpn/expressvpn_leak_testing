from xv_leak_tools.test_components.network_configuration.network_configuration_step import NetworkConfigurationStep

class EnsureIPv6(NetworkConfigurationStep):

    def setup(self, device):
        # TODO: Use a different exception type to distinguish unable to run from test failures.
        self.assertNotEmpty(
            device["ip_tool"].public_ipv6_addresses(),
            "This test requires an IPv6 connection")

# Expose the step
Step = EnsureIPv6
