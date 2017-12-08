from desktop_local_tests.disrupter import Disrupter
from xv_leak_tools.log import L

class WindowsEnableNewAdapterDisrupter(Disrupter):

    def __init__(self, device, parameters):
        super().__init__(device, parameters)
        self._restrict_parameters(must_disrupt=True, must_restore=False)
        self._primary_adapter = self._find_primary_adapter()

    def _find_primary_adapter(self):
        adapters = self._device['network_tool'].adapters_in_priority_order()
        primary_adapter = [adapter for adapter in adapters if adapter.pingable()][0]
        L.info("Primary network adapter is {}".format(primary_adapter.name()))
        return primary_adapter

    def setup(self):
        L.describe('Disable the primary network adapter')
        self._primary_adapter.disable()
        L.info("Disabled adapter {}".format(self._primary_adapter.name()))

    def disrupt(self):
        # Slightly confusing, but the disrupt-ion step here is actually enabling the adapter, not
        # disabling it.
        L.describe('Re-enable primary network adapter')
        self._primary_adapter.enable()

    def teardown(self):
        if self._primary_adapter:
            self.disrupt()
        super().teardown()
