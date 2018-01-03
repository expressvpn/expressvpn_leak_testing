from desktop_local_tests.local_ip_responder_test_case_with_disrupter import LocalIPResponderTestCaseWithDisrupter
from desktop_local_tests.linux.linux_interface_disrupter import LinuxInterfaceDisrupter

class TestLinuxIPResponderDisruptInterface(LocalIPResponderTestCaseWithDisrupter):

    # TODO: Docs

    def __init__(self, devices, parameters):
        super().__init__(LinuxInterfaceDisrupter, devices, parameters)
