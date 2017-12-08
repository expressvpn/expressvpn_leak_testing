# pylint: skip-file

import os
from xv_leak_tools import tools_root

DEVICES = [
    # If you wish to customize localhost then you can specify parameters here like so. Local host is
    # always available so it's not necessary to specify it in the device inventory.
    {
        'device_id': 'localhost',
        'discovery_type': 'localhost',
        # Specify the port spanning interface if the local device is also being used to process
        # packets captured on a port span
        'span_interface': 'en9',
        # The git_root defaults to the root of the tools. However, if you wish to customize the
        # tools then you might want to do so by making the tools a submodule of another repo (which
        # is how ExpressVPN does it). In that situation you can specify a different git_root which
        # will recursively update that repo and thus these tools as well.
        'git_root': os.path.join(tools_root()),
    },
    # Here's an example of how to specify a static device, i.e. a physical device with a static
    # ip address.
    {
        # device_id ID must be unique across all devices
        'device_id': 'windows10_static',
        # discovery_type tells the tools how this device should be accessed.
        'discovery_type': 'static',
        # List the IP addresses of the device here. They will be used for SSH.
        'ips': [],
        # Tell the tools what OS this device is. It uses that information to decide if the device is
        # usable for a specific test
        'os_name' : 'windows',
        'os_version' : '10',
        'username': 'xv_leak_tools',
        'password': None,
        # SSH key for accessing the device
        # TODO: Check that this would be picked up by default
        'ssh_key': os.path.join('~/.ssh', 'ssh_keys', 'id_rsa'),
        'ssh_password': None,
        'output_root': '/home/xv_leak_tools/xv_leak_tools_output',
        'tools_root': '/home/xv_leak_tools/xv_leak_testing',
        # TODO: Still necessary?
        'tools_user': 'xv_leak_tools',
    },
    # Here's an example of how to specify a VMWare image as a device. Most of the keys are the same
    # as a static device. One notable difference is that IPs are not necessary as the vmware tools
    # can determine the IP of the device once the vm image is loaded.
    {
        'device_id': 'macos10.12_vmware',
        # discovery_type is specifying vmware this time.
        'discovery_type': 'vmware',
        'vmx_path': '/path/to/vmware/images/macOS 10.12.vmwarevm',
        # Snapshots allow you to use the same image for multiple test setups
        'vm_snapshot': 'Snapshot To Use',
        'os_name' : 'macos',
        'os_version' : '10.12',
        'username': 'xv_leak_tools',
        'password': None,
        'ssh_key': os.path.join('~/.ssh', 'ssh_keys', 'id_rsa'),
        'ssh_password': None,
        'output_root': '/Users/xv_leak_tools/xv_leak_tools_output',
        'tools_root': '/Users/xv_leak_tools/xv_leak_testing',
        'tools_user': 'xv_leak_tools',
    },
]
