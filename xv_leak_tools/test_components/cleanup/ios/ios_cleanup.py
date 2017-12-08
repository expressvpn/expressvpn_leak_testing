from xv_leak_tools.log import L
from xv_leak_tools.test_components.cleanup.cleanup import Cleanup

class IOSCleanup(Cleanup):

    def cleanup(self):
        L.warning("No cleanup implemented for iOS yet!")
