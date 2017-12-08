from abc import ABCMeta, abstractmethod

from xv_leak_tools.test_components.component import Component

class Cleanup(Component, metaclass=ABCMeta):

    @abstractmethod
    def cleanup(self):
        pass
