from xv_leak_tools.test_components.cleanup.cleanup_builder import CleanupBuilder

def register(factory):
    factory.register(CleanupBuilder())
