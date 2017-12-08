from xv_leak_tools.factory import Builder
from xv_leak_tools.test_components.git.git import Git

class GitBuilder(Builder):

    @staticmethod
    def name():
        return "git"

    def build(self, device, config):
        # LocalComponent will handle this not working on non-desktop devices.

        # TODO: This needs to work remotely as we may want to git checkout other desktop machines
        # which are being used in tests
        return Git(device, config)
