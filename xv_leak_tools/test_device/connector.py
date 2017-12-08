from abc import ABCMeta, abstractmethod
class Connector(metaclass=ABCMeta):

    @abstractmethod
    def execute(self, cmd, root=False):
        pass

    @abstractmethod
    def push(self, src, dst):
        pass

    @abstractmethod
    def pull(self, src, dst):
        pass
