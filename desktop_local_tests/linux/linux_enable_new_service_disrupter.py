from desktop_local_tests.disrupter import Disrupter
from xv_leak_tools.log import L

class LinuxEnableNewServiceDisrupter(Disrupter):

    def __init__(self, device, parameters):
        super().__init__(device, parameters)
        self._restrict_parameters(must_disrupt=True, must_restore=False)
        self._primary_service = None

    def setup(self):
        L.describe('Disable the primary network service')
        services = self._device['network_tool'].network_services_in_priority_order()
        self._primary_service = [service for service in services if service.active()][0]
        self._primary_service.disable()
        L.info("Disabled service {}".format(self._primary_service.name()))

    def disrupt(self):
        # Slightly confusing, but the disrupt-ion step here is actually enabling the service, not
        # disabling it.
        L.describe('Re-enable primary network service')
        self._primary_service.enable()

    def teardown(self):
        if self._primary_service:
            self._primary_service.enable()
        super().teardown()
