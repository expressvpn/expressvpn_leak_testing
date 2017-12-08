from xv_leak_tools.factory import Builder
from xv_leak_tools.test_components.ip_responder.ip_responder import IPResponder

class IPResponderBuilder(Builder):

    @staticmethod
    def name():
        return 'ip_responder'

    def build(self, device, config):
        return IPResponder(device, config)
