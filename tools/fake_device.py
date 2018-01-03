import os

from xv_leak_tools.import_helpers import import_by_filename
from xv_leak_tools.test_device.device_discoverers.localhost_discoverer import LocalhostDiscoverer
from xv_leak_tools.test_execution.test_run_context import TestRunContext

def get_fake_device():
    context_dict = import_by_filename('default_context.py').CONTEXT
    context_dict['output_directory'] = os.path.expanduser("~/temp")
    context = TestRunContext(context_dict)
    device = LocalhostDiscoverer(context, {}).discover_device({'device_id': 'localhost'})
    return device
