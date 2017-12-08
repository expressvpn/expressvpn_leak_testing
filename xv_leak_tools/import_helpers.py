import importlib
import os
import pkgutil

from xv_leak_tools.exception import XVEx
from xv_leak_tools.helpers import other_oses
from xv_leak_tools.log import L

def import_by_filename(filename):
    L.debug("Importing by filename: {}".format(filename))
    spec = importlib.util.spec_from_file_location("", filename)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def _iter_package(package, restrict_platform=True, is_pkg=True):
    def ignore_package(package, ignore_substrings):
        # Don't import anything which doesn't belong on this OS
        for ignore in ignore_substrings:
            if ignore in package:
                return True
        return False

    if restrict_platform and ignore_package(package, other_oses()):
        return

    try:
        L.debug("Importing {}".format(package))
        mod = importlib.import_module(package)
        package_path = os.path.normpath(os.path.split(mod.__file__)[0])
        yield mod
    except ImportError as ex:
        raise XVEx(
            "Can't import package '{}' ({}). Make sure the package directory is in your "
            "sys.path".format(package, ex))

    if not is_pkg:
        return

    L.verbose("Walking package path {}".format(package_path))
    for _, module_name, is_pkg2 in pkgutil.walk_packages([package_path]):
        for mod in _iter_package("{}.{}".format(package, module_name), restrict_platform, is_pkg2):
            yield mod

def import_all_from_package(package, restrict_platform=True):
    for mod in _iter_package(package, restrict_platform):
        L.verbose("Imported {}".format(mod.__file__))

def itersubclasses(cls, _seen=None):
    if not isinstance(cls, type):
        raise TypeError('itersubclasses must be called with '
                        'new-style classes, not %.100r' % cls)
    if _seen is None:
        _seen = set()
    try:
        subclasses = cls.__subclasses__()
    except TypeError: # fails only when cls is type
        subclasses = cls.__subclasses__(cls)
    for subclass in subclasses:
        if subclass not in _seen:
            _seen.add(subclass)
            yield subclass
            for subsubclass in itersubclasses(subclass, _seen):
                yield subsubclass

def class_by_name(name, base_class):
    available = []
    for subclass in itersubclasses(base_class):
        if subclass.__name__ == name:
            return subclass
        available.append(subclass)
    raise XVEx("Couldn't find class {} deriving from {}. Available classes:\n{}".format(
        name, base_class, "\n".join([clazz.__name__ for clazz in available])))
