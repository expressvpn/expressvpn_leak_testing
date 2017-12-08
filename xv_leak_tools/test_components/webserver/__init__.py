from xv_leak_tools.test_components.webserver.webserver_builder import WebserverBuilder

def register(factory):
    factory.register(WebserverBuilder())
