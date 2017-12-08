from xv_leak_tools.test_components.settings.settings_builder import SettingsBuilder

def register(factory):
    factory.register(SettingsBuilder())
