from desktop_local_tests.disrupter import Disrupter
from xv_leak_tools.log import L

class MacOSInterfaceDisrupter(Disrupter):

    def __init__(self, device, parameters):
        super().__init__(device, parameters)
        self._restrict_parameters(must_disrupt=True)

        self.primary_service = self._find_primary_service()

    def _find_primary_service(self):
        services = self._device['network_tool'].network_services_in_priority_order()
        primary_service = [service for service in services if service.active()][0]
        L.info("Primary network service {} has interface {}".format(
            primary_service.name(), primary_service.interface()))
        return primary_service

    def disrupt(self):
        L.describe("Disable the primary network service's interface")
        self.primary_service.disable_interface()

    def restore(self):
        L.describe("Enable the primary network service's interface")
        self.primary_service.enable_interface()

    def teardown(self):
        if self.primary_service:
            self.primary_service.enable_interface()

        super().teardown()
