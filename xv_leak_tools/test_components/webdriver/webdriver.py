import time
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from xv_leak_tools.log import L
from xv_leak_tools.manual_input import message_and_await_enter

from xv_leak_tools.exception import XVEx
from xv_leak_tools.test_components.local_component import LocalComponent

# The Webdriver component is effectively a factory in itself. There will likely be tests which need
# to create more than one webdriver, so the tests use this component to create drivers as they need
# them.

class XVDriverLinux(LocalComponent):

    def __init__(self, device, config):
        super().__init__(device, config)
        self._server_running = False

    def __del__(self):
        self._kill_server()

    def _start_server(self):
        L.warning("The server must be started manually :(")
        if self._device.connector().execute(['lsof', '-t', '-i', ':4444'])[0]:
            message_and_await_enter("Start the Selenium server")
            while self._device.connector().execute(['lsof', '-t', '-i', ':4444'])[0]:
                L.debug("Waiting for Selenium")
                time.sleep(0.5)
        self._server_running = True

    def _kill_server(self):
        if self._server_running:
            L.debug("Killing Selenium server")
            selenium_process = self._device.connector().execute(['lsof', '-t', '-i', ':4444'])
            if not selenium_process[0]:
                selenium_pid = selenium_process[1].strip()
                self._device.connector().execute(['kill', selenium_pid])
                self._server_running = False
            else:
                L.warning("Couldn't find the Selenium server process; try killing Java")

    def driver(self, browser):
        self._start_server()
        command_executor = 'http://127.0.0.1:4444/wd/hub'

        if browser == 'firefox':
            return webdriver.Remote(command_executor=command_executor,
                                    desired_capabilities=DesiredCapabilities.FIREFOX)
        if browser == 'chrome':
            return webdriver.Remote(command_executor=command_executor,
                                    desired_capabilities=DesiredCapabilities.CHROME)
        if browser == 'phantom':
            return webdriver.PhantomJS()
        raise XVEx("{} is not supported on {}".format(browser, self._device.os_name()))

class XVDriverMacOS(LocalComponent):

    def driver(self, browser):
        if browser == 'firefox':
            return webdriver.Firefox()
        if browser == 'chrome':
            return webdriver.Chrome()
        if browser == 'safari':
            return webdriver.Safari()
        if browser == 'opera':
            return webdriver.Opera()
        if browser == 'phantom':
            return webdriver.PhantomJS()
        raise XVEx("{} is not supported on {}".format(browser, self._device.os_name()))

class XVDriverWindows(LocalComponent):

    def driver(self, browser):
        if browser == 'firefox':
            return webdriver.Firefox()
        if browser == 'chrome':
            return webdriver.Chrome('chromedriver.exe')
        if browser == 'opera':
            # TODO: Opera implementation is quite buggy annoyingly. It won't close at the moment
            # Need to investigate.
            options = webdriver.ChromeOptions()
            options.binary_location = "C:\\Program Files\\Opera\\launcher.exe"
            return  webdriver.Opera(executable_path='operadriver.exe', opera_options=options)
        if browser == 'ie':
            return webdriver.Ie()
        if browser == 'edge':
            # TODO: check for Windows < 8.1?
            return webdriver.Edge()
        if browser == 'phantom':
            return webdriver.PhantomJS()
        raise XVEx("{} is not supported on {}".format(browser, self._device.os_name()))
