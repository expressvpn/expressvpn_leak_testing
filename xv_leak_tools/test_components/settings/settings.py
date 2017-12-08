from xv_leak_tools.exception import XVEx
from xv_leak_tools.manual_input import message_and_await_enter
from xv_leak_tools.test_components.component import Component

class Settings(Component):

    # pylint: disable=no-self-use

    def enable_wifi(self):
        message_and_await_enter('Enable WiFi')

    def disable_wifi(self):
        message_and_await_enter('Disable WiFi')

    def toggle_wifi(self):
        raise XVEx('Toggling settings is not implemented')

    def enable_mobile_data(self):
        message_and_await_enter('Enable data')

    def disable_mobile_data(self):
        message_and_await_enter('Disable data')

    def toggle_mobile_data(self):
        raise XVEx('Toggling settings is not implemented')

    def enable_airplane_mode(self):
        message_and_await_enter('Enable airplane mode')

    def disable_airplane_mode(self):
        message_and_await_enter('Disable airplane mode')

    def toggle_airplane_mode(self):
        raise XVEx('Toggling settings is not implemented')

    def enable_wired(self):
        message_and_await_enter('Plug in wired internet')

    def disable_wired(self):
        message_and_await_enter('Plug out wired internet')

    def toggle_wired(self):
        raise XVEx('Toggling settings is not implemented')
