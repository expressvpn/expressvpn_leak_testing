from abc import ABCMeta, abstractmethod

from xv_leak_tools.test_components.component import Component

class Firewall(Component, metaclass=ABCMeta):

    '''Super simple class for now. It's very focused on us blocking the VPN server IP. Nothing
    more complex needed yet.'''

    @abstractmethod
    def block_ip(self, ip):
        pass

    @abstractmethod
    def unblock_ip(self, ip):
        pass
