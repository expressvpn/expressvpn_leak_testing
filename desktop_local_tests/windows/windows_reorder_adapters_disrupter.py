from xv_leak_tools.log import L
from xv_leak_tools.exception import XVEx
from desktop_local_tests.disrupter import Disrupter

class WindowsReorderAdaptersDisrupter(Disrupter):

    def __init__(self, device, parameters):
        super().__init__(device, parameters)
        self._restrict_parameters(must_disrupt=True, must_restore=False)
        # TODO: Does this really exclude all adapters we don't want? Maybe exclude TAP somehow?
        adapters = self._device['network_tool'].adapters_in_priority_order()
        L.verbose("All adapters: {}".format(adapters))
        adapters = [adapter for adapter in adapters if adapter.pingable()]
        L.verbose("Pingable adapters: {}".format(adapters))
        if len(adapters) < 2:
            raise XVEx("There must be at least 2 pingable adapters. All pingable adapters are {}"
                       .format(adapters))
        self._adapter1 = adapters[0]
        self._adapter2 = adapters[1]
        self._adapter1_original_metric = self._adapter1.interface_metric()
        self._adapter2_original_metric = self._adapter2.interface_metric()

    def setup(self):
        super().setup()
        # TODO: Hardcoded 1 and 1000. Does it matter?
        self._adapter1.set_interface_metric(1)
        L.describe("Set interface metric for adapter {} to {}".format(self._adapter1.name(), 1))
        self._adapter2.set_interface_metric(1000)
        L.describe("Set interface metric for adapter {} to {}".format(self._adapter2.name(), 1000))

    @staticmethod
    def _swap_adapters(adapter1, adapter2):
        temp = adapter1.interface_metric()
        adapter1.set_interface_metric(adapter2.interface_metric())
        adapter2.set_interface_metric(temp)
        L.info("Swapped interface metric for adapters: {} -> {}".format(
            adapter1.name(), adapter2.name()))

    def _swap_highest_priority_adapters(self):
        WindowsReorderAdaptersDisrupter._swap_adapters(self._adapter1, self._adapter2)

    def disrupt(self):
        L.describe('Swap the two highest-priority active network services')
        self._swap_highest_priority_adapters()

    def teardown(self):
        L.info("Restoring interface metrics")
        self._adapter1.set_interface_metric(self._adapter1_original_metric)
        self._adapter2.set_interface_metric(self._adapter2_original_metric)
        super().teardown()
