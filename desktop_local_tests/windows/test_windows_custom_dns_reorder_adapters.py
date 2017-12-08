from desktop_local_tests.local_custom_dns_test_case_with_disrupter import LocalCustomDNSTestCaseWithDisrupter
from desktop_local_tests.windows.windows_reorder_adapters_disrupter import WindowsReorderAdaptersDisrupter

class TestWindowsCustomDNSDisruptReorderAdapters(LocalCustomDNSTestCaseWithDisrupter):

    def __init__(self, devices, parameters):
        super().__init__(WindowsReorderAdaptersDisrupter, devices, parameters)
