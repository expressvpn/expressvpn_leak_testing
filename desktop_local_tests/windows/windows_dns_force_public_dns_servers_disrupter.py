from desktop_local_tests.disrupter import Disrupter
from xv_leak_tools.log import L
from xv_leak_tools.manual_input import message_and_await_enter

class WindowsDNSForcePublicDNSServersDisrupter(Disrupter):

    def __init__(self, device, parameters):
        super().__init__(device, parameters)
        self._restrict_parameters(must_disrupt=True, must_restore=False, must_wait=False)
        self._primary_adapter = self._find_primary_adapter()
        self._has_disrupted = False

    def _find_primary_adapter(self):
        primary_adapter = self._device['network_tool'].primary_adapter()
        L.info("Primary network adapter is {}".format(primary_adapter.name()))
        return primary_adapter

    def disrupt(self):
        self._has_disrupted = True
        message_and_await_enter("Set the DNS servers for adapter {} ({}) to 8.8.8.8".format(
            self._primary_adapter.name(), self._primary_adapter.net_connection_id()))

    def teardown(self):
        if self._has_disrupted:
            message_and_await_enter("Reset the DNS servers for adapter {} ({})".format(
                self._primary_adapter.name(), self._primary_adapter.net_connection_id()))
        super().teardown()
