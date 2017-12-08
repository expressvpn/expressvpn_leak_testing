from desktop_local_tests.disrupter import Disrupter
from xv_leak_tools.log import L

# TODO: Docs wrong
class MacOSDNSForcePublicDNSServersDisrupter(Disrupter):

    def __init__(self, device, parameters):
        super().__init__(device, parameters)
        self._restrict_parameters(must_disrupt=True, must_restore=False, must_wait=False)

        self.primary_service = self._find_primary_service()
        # Preserve the DNS servers *before* we connect to the VPN. This disruption test isn't
        # designed to set the DNS servers then unset them whilst connected, i.e. there's no
        # restore method. So when the test ends we want to ensure the DNS servers are back as they
        # were to beging with
        self.original_dns_servers = self.primary_service.dns_servers(include_dhcp_servers=False)

    def _find_primary_service(self):
        services = self._device['network_tool'].network_services_in_priority_order()
        primary_service = [service for service in services if service.active()][0]
        L.info("Primary network service is {}".format(primary_service.name()))
        return primary_service

    def _restore_dns_servers(self):
        if self.original_dns_servers:
            self.primary_service.set_dns_servers(self.original_dns_servers)
        else:
            self.primary_service.set_dns_servers(['Empty'])

    def disrupt(self):
        # Don't use Google. Make the DNS servers stand out but using one's that probably won't be
        # used often.
        # TODO: Make configurable?
        L.describe('Set the primary service DNS servers to public DNS servers')
        self.primary_service.set_dns_servers(['37.235.1.174', '37.235.1.177'])

    def teardown(self):
        self._restore_dns_servers()
        super().teardown()
