from xv_leak_tools.test_framework.test_case import TestCase
from xv_leak_tools.log import L

class TestFail(TestCase):
    """Dummy test case for testing library functionality. This test does nothing other than
    deliberately fail."""

    def test(self):
        L.info("This test does nothing but fail")
        L.describe("Deliberately fail test")
        self.assertTrue(False)
