import importlib

from abc import ABCMeta, abstractmethod

from xv_leak_tools.exception import XVEx
from xv_leak_tools.log import L

class Builder(metaclass=ABCMeta):

    def __init__(self):
        self._base_builder = None

    def set_base_builder(self, base_builder):
        self._base_builder = base_builder

    @abstractmethod
    def build(self, device, config):
        pass

# This is a very basic factory. We could adapt it in a bunch of ways such as:
# * Allow it to take typed Builders other than Builder, e.g. a particular factory will only allow
#   builder class X and enforce it.
# * Similarly we could enforce builders to return a specific type of class as well.
class Factory:

    def __init__(self, modules):
        self._builders = {}
        self._register_builders(modules)

    def _register_builders(self, modules):
        for module in modules:
            mod = importlib.import_module(module)
            if not hasattr(mod, 'register'):
                raise XVEx(
                    "Module {} has no method 'register'. It can't be used in a factory".format(
                        module))
            mod.register(self)

    def register(self, builder):
        if not isinstance(builder, Builder):
            raise XVEx(
                "Class {} does not derive from Builder class. Can't register it with "
                "Factory".format(builder.__class__.__name__))

        # TODO: This check might not work if the method is on a base class.
        if not hasattr(builder.__class__, "name"):
            raise XVEx(
                "Builder class {} does not provide a class method 'name'. It must do so in order to"
                "identify what it builds".format(builder.__class__.__name__))

        name = builder.__class__.name()

        existing_builder = self.builder(name)
        if existing_builder is not None:
            L.info("Builder {} already exists. Replacing it with new builder".format(name))
            builder.set_base_builder(existing_builder)

        self._builders[name] = builder

    def builder(self, name):
        return self._builders.get(name, None)

    def builder_names(self):
        return self._builders.keys()

    # Build is currently specialised to building "things" for a device. We could generalise and
    # have build (and the Builder's build method) take *args, **kargs. But for now let's stay
    # specialised to our needs.
    def build(self, name, device, config):
        return self._builders[name].build(device, config)
