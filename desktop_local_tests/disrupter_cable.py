from desktop_local_tests.disrupter import Disrupter
from xv_leak_tools.log import L
from xv_leak_tools.manual_input import message_and_await_enter

class DisrupterCable(Disrupter):

    PULL_MESSAGE = '''\
Pull the ethernet cable.
If you're using a VM then you can simulate this by disconnecting the network adapter from the VM \
settings.
NOTE: You should press enter BEFORE pulling the cable to maximize the chance of detecting a leak.
'''

    PLUG_MESSAGE = 'Replace the ethernet cable.  You should press enter ' \
                   'BEFORE replacing the cable to maximize the chance of detecting a leak.'

    def __init__(self, device, parameters):
        super().__init__(device, parameters)
        self._restrict_parameters(must_disrupt=True)
        self._pull = self._parameters.get("pull", True)

    def setup(self):
        # TODO: This should be done with a network configuration step
        msg = "Ensure you have an Ethernet (wired) connection and at least one " \
              "other network service, e.g. Wi-Fi\n"
        if not self._pull:
            msg += "Ensure that the cable is UNPLUGGED."
        message_and_await_enter(msg)

    def disrupt(self):
        msg = DisrupterCable.PULL_MESSAGE if self._pull else DisrupterCable.PLUG_MESSAGE
        L.describe(msg)
        message_and_await_enter(msg)

    def restore(self):
        msg = "Ensure the ethernet cable is plugged back in"
        L.describe(msg)
        message_and_await_enter(msg)

    def teardown(self):
        self.restore()
        super().teardown()
