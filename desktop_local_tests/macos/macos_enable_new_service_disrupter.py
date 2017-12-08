from desktop_local_tests.disrupter import Disrupter
from xv_leak_tools.log import L

class MacOSEnableNewServiceDisrupter(Disrupter):

    def __init__(self, device, parameters):
        super().__init__(device, parameters)
        self._restrict_parameters(must_disrupt=True, must_restore=False)
        self._primary_service = None

    def setup(self):
        # TODO: This should really be in the network config steps.
        L.describe('Ensure there are two active network services')
        services = self._device['network_tool'].network_services_in_priority_order()
        active_services = [service for service in services if service.active()]
        self.assertGreaterEqual(
            len(active_services), 2,
            "Need two active network services to run this test. Only the following are "
            "active: {}".format(active_services))

        L.describe('Disable the primary network service')
        self._primary_service = active_services[0]
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
