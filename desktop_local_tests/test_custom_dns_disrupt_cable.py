from desktop_local_tests.local_custom_dns_test_case_with_disrupter import LocalCustomDNSTestCaseWithDisrupter
from desktop_local_tests.disrupter_cable import DisrupterCable

class TestCustomDNSDisruptCable(LocalCustomDNSTestCaseWithDisrupter):

    def __init__(self, devices, parameters):
        super().__init__(DisrupterCable, devices, parameters)
