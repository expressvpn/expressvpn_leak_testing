from xv_leak_tools.test_device.connector import Connector
from xv_leak_tools.log import L

class DummyConnector(Connector):

    def __init__(self):
        L.warning('Using dummy connector')

    @staticmethod
    def push(src, dst):
        L.debug('{} --> {}'.format(src, dst))

    def pull(self, src, dst):
        self.push(dst, src)

    @staticmethod
    def execute(cmd, root=False):
        L.debug('Run {}{}'.format(' '.join(cmd), root * ' as root'))
        return 0, '', ''
