from xv_leak_tools.test_framework.test_case import TestCase
from xv_leak_tools.log import L

class TestPass(TestCase):
    """Dummy test case for testing library functionality. This test does nothing other than
    deliberately pass."""

    def test(self):
        L.info("This test does nothing but pass")
        L.describe("Deliberately pass test")
        self.assertTrue(True)
