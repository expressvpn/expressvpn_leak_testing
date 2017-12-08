from xv_leak_tools.test_components.network_configuration.network_configuration_step import NetworkConfigurationStep

class EnsureLocalDNS(NetworkConfigurationStep):

    def setup(self, device):
        dns_servers = device["dns_tool"].known_servers()
        for dns_server in dns_servers:
            if dns_server.is_private:
                return

        # TODO: Use a different exception type to distinguish unable to run from test failures.
        self.assertTrue(
            False,
            "This test requires a DNS server with a local IP. Available DNS servers are: {}".format(
                dns_servers))

# Expose the step
Step = EnsureLocalDNS
