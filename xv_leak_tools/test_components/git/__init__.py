from xv_leak_tools.test_components.git.git_builder import GitBuilder

def register(factory):
    factory.register(GitBuilder())
