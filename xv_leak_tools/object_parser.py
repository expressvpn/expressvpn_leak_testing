import json

from xv_leak_tools.exception import XVEx
from xv_leak_tools.helpers import exception_to_string
from xv_leak_tools.import_helpers import import_by_filename
from xv_leak_tools.log import L

def object_from_json_string(json_string, _):
    return json.loads(json_string)

def object_from_json_file(filename, _):
    with open(filename) as file_:
        return json.loads(file_.read())

def object_from_python_module(filename, attribute_name):
    module = import_by_filename(filename)
    if not hasattr(module, attribute_name):
        raise XVEx("'{}' should have an attribute called '{}'".format(
            filename, attribute_name))
    return getattr(module, attribute_name)

def object_from_command_line(source, attribute_name):
    L.debug("Trying to convert '{}' to an object (attribute_name={})".format(
        source, attribute_name))

    # Order here is the "most likely" order we'll get objects
    funcs = [
        object_from_python_module,
        object_from_json_file,
        object_from_json_string,
    ]

    all_errors = ""
    for func in funcs:
        try:
            return func(source, attribute_name)
        except Exception as ex: # pylint: disable=broad-except
            all_errors += "{} failed due to: {}\n".format(func.__name__, exception_to_string(ex))

    raise XVEx("Couldn't convert '{}' to a valid object:\n{}".format(source, all_errors))
