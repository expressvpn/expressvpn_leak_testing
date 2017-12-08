from xv_leak_tools import tools_root
from xv_leak_tools.log import L
from xv_leak_tools.process import check_subprocess
from xv_leak_tools.test_components.local_component import LocalComponent
from xv_leak_tools.test_device.connector_helper import ConnectorHelper

class Git(LocalComponent):

    @staticmethod
    def _git_branch():
        '''Return the git branch we're currently on. This is designed to run on the test
        orchestration device, i.e. localhost. We use it to ensure that all devices are checked out
        to the same revision'''
        # TODO: Consider making this configurable as well, with the default being this.
        return check_subprocess(['git', 'rev-parse', '--abbrev-ref', 'HEAD'])[0].strip()

    def setup(self):
        if not self._config.get("checkout", False):
            return

        # Update the device's git checkout to be the same as our branch and to be at latest revision
        branch = Git._git_branch()
        L.info(
            "Updating git repo to branch {} on device {}".format(branch, self._device.device_id()))
        connector_helper = ConnectorHelper(self._device)

        git_root = self._device.config().get('git_root', tools_root())

        # TODO: Potentially should clean as well?
        connector_helper.execute_command(
            [
                # This can possibly be done in fewer lines
                'cd', git_root, '&&',
                'git', 'checkout', branch, '&&',
                'git', 'pull', '&&',
                'git', 'submodule', 'update', '--init', '--recursive'
            ]
        )
