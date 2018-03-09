from desktop_local_tests.disrupter import Disrupter
from xv_leak_tools.log import L

class WindowsAdapterDisrupter(Disrupter):

    def __init__(self, device, parameters):
        super().__init__(device, parameters)
        self._restrict_parameters(must_disrupt=True)
        self._primary_adapter = self._find_primary_adapter()

    def _find_primary_adapter(self):
        primary_adapter = self._device['network_tool'].primary_adapter()
        L.info("Primary network adapter is {}".format(primary_adapter.name()))
        return primary_adapter

    def disrupt(self):
        L.describe('Disable the primary network adapter')
        self._primary_adapter.disable()

    def restore(self):
        L.describe('Re-enable the primary network adapter')
        self._primary_adapter.enable()

    def teardown(self):
        if self._primary_adapter:
            self._primary_adapter.enable()

        super().teardown()
