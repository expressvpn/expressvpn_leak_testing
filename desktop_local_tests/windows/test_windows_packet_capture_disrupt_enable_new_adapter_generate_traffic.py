from desktop_local_tests.local_packet_capture_test_case_with_disrupter_and_generator import LocalPacketCaptureTestCaseWithDisrupterAndGenerator
from desktop_local_tests.windows.windows_enable_new_adapter_disrupter import WindowsEnableNewAdapterDisrupter

class TestWindowsPacketCaptureDisruptEnableNewAdapterAndGenerateTraffic(
        LocalPacketCaptureTestCaseWithDisrupterAndGenerator):

    # TODO: Docs

    def __init__(self, devices, parameters):
        super().__init__(WindowsEnableNewAdapterDisrupter, devices, parameters)
