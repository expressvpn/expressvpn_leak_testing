from desktop_local_tests.local_ip_responder_test_case_with_disrupter import LocalIPResponderTestCaseWithDisrupter
from desktop_local_tests.linux.linux_enable_new_service_disrupter import LinuxEnableNewServiceDisrupter

class TestLinuxIPResponderDisruptEnableNewService(LocalIPResponderTestCaseWithDisrupter):

    # TODO: Docs

    def __init__(self, devices, config):
        super().__init__(LinuxEnableNewServiceDisrupter, devices, config)
