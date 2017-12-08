import importlib
# from xv_leak_tools.log import L
from xv_leak_tools.test_components.local_component import LocalComponent

class NetworkConfiguration(LocalComponent):

    def __init__(self, device, config):
        super().__init__(device, config)
        self._steps = []
        for step in self._config.get("steps", []):
            package = "xv_leak_tools.test_components.network_configuration.steps.{}".format(step)
            module = importlib.import_module(package)
            self._steps.append(module.Step())

    def setup(self):
        for step in self._steps:
            step.setup(self._device)

    def teardown(self):
        for step in self._steps:
            step.teardown(self._device)
