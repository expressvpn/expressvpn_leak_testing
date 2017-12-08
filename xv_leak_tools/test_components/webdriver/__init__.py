from xv_leak_tools.test_components.webdriver.webdriver_builder import WebdriverBuilder

def register(factory):
    factory.register(WebdriverBuilder())
