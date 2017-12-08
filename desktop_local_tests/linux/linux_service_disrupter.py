from desktop_local_tests.disrupter import Disrupter
from xv_leak_tools.log import L

class LinuxServiceDisrupter(Disrupter):
    def __init__(self, devices, parameters):
        super().__init__(devices, parameters)
        self._restrict_parameters(must_disrupt=True)
        self.primary_service = self._find_primary_service()

    def _find_primary_service(self):
        services = self._device['network_tool'].network_services_in_priority_order()
        primary_service = [service for service in services if service.active()][0]
        L.info("Primary network service is {}".format(primary_service.name()))
        return primary_service

    def disrupt(self):
        L.describe('Disable the primary network service')
        self.primary_service.disable()

    def restore(self):
        L.describe('Re-enable the primary network service')
        self.primary_service.enable()

    def teardown(self):
        if self.primary_service:
            self.primary_service.enable()

        super().teardown()
