from xv_leak_tools.factory import Builder
from xv_leak_tools.test_components.webserver.webserver import WebServer

class WebserverBuilder(Builder):

    @staticmethod
    def name():
        return 'webserver'

    def build(self, device, config):
        return WebServer(device, config)
