from desktop_local_tests.disrupter import Disrupter
from xv_leak_tools.log import L

class LinuxInterfaceDisrupter(Disrupter):

    def __init__(self, devices, parameters):
        super().__init__(devices, parameters)
        self._restrict_parameters(must_disrupt=True)
        self.primary_service = self._find_primary_service()

    def _find_primary_service(self):
        services = self._device['network_tool'].network_services_in_priority_order()
        primary_service = [service for service in services if service.active()][0]
        primary_interface = primary_service.interface()
        L.info("Primary network service is {}, with interface {}".format(
            primary_service.id(), primary_interface))
        return primary_service

    def disrupt(self):
        L.describe('Disable the primary interface (with ifconfig)')
        self.primary_service.disable_interface()

    def restore(self):
        L.describe('Reenable the primary interface (with ifconfig)')
        self.primary_service.enable_interface()

    def teardown(self):
        if self.primary_service:
            self.primary_service.enable_interface()

        super().teardown()
