from xv_leak_tools.test_components.dns_tool.dns_lookup_tool import DNSLookupTool

class MacOSDNSTool(DNSLookupTool):

    # pylint: disable=no-self-use

    # N.B. This doesn't work remotely when why we are a LocalComponent
    def known_servers(self):
        # Import here to allow the file to be imported on any OS
        from xv_leak_tools.network.macos.locations_and_services import MacOSNetwork

        dns_servers = MacOSNetwork.dns_servers()
        # Quick sanity check
        self._check_current_dns_server_is_known(dns_servers)
        return dns_servers
