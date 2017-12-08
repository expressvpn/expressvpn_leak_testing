import os
import time

from xv_leak_tools import tools_user
from xv_leak_tools.exception import XVEx
from xv_leak_tools.helpers import current_os, TimeUp
from xv_leak_tools.log import L
from xv_leak_tools.process import check_subprocess, XVProcessException
from xv_leak_tools.test_device.create_device import create_device
from xv_leak_tools.test_device.device_discoverers.device_discoverer import DeviceDiscoverer
from xv_leak_tools.test_device.simple_ssh_connector import SimpleSSHConnector

class VMWareDeviceDiscoverer(DeviceDiscoverer):

    def __init__(self, context, device_inventory):
        super().__init__(context, device_inventory)
        self._vms_in_use = set()

    @staticmethod
    def discovery_type():
        return 'vmware'

    @staticmethod
    def _vmrun_path():
        if current_os() == 'macos':
            return '/Applications/VMware Fusion.app/Contents/Library/vmrun'
        raise XVEx("TODO: Implement VMWare support for OS '{}'".format(current_os()))

    @staticmethod
    # TODO: How/when are we vmx_path to stop VMs?
    def _start_vm(vmx_path):
        cmd = [VMWareDeviceDiscoverer._vmrun_path(), 'start', vmx_path]
        check_subprocess(cmd)

    @staticmethod
    def _pause_vm(vmx_path):
        cmd = [VMWareDeviceDiscoverer._vmrun_path(), 'pause', vmx_path]
        check_subprocess(cmd)

    @staticmethod
    def _unpause_vm(vmx_path):
        cmd = [VMWareDeviceDiscoverer._vmrun_path(), 'unpause', vmx_path]
        check_subprocess(cmd)

    @staticmethod
    def _stop_vm(vmx_path):
        cmd = [VMWareDeviceDiscoverer._vmrun_path(), 'stop', vmx_path]
        check_subprocess(cmd)

    @staticmethod
    def _vm_state(vmx_path):
        cmd = [VMWareDeviceDiscoverer._vmrun_path(), 'checkToolsState', vmx_path]
        return check_subprocess(cmd)[0].strip()

    @staticmethod
    def _revert_vm_to_snapshot(vmx_path, snapshot):
        cmd = [VMWareDeviceDiscoverer._vmrun_path(), 'revertToSnapshot', vmx_path, snapshot]
        check_subprocess(cmd)

    @staticmethod
    def _get_vm_ip(vmx_path):
        cmd = [VMWareDeviceDiscoverer._vmrun_path(), 'getGuestIPAddress', vmx_path]
        return check_subprocess(cmd)[0].strip()

    @staticmethod
    def _wait_for_vm_power(vmx_path):
        # Hacky trick to make sure VM has power
        timeup = TimeUp(60)
        while not timeup:
            try:
                if VMWareDeviceDiscoverer._vm_state(vmx_path) != 'running':
                    time.sleep(0.2)
                    continue
                VMWareDeviceDiscoverer._get_vm_ip(vmx_path)
                # If we manage to get the IP then we're powered on. This will be unlikely to happen
                break
            except XVProcessException as ex:
                if 'The virtual machine is not powered on' in ex.stdout:
                    time.sleep(0.2)
                    continue
                # Any other exception means we're powered on
                break
        if timeup:
            raise XVEx("VM never got power: {}".format(vmx_path))
        L.verbose('VM now has power')

    @staticmethod
    def _chown_vm_files(vmx_path):
        '''We usually run the test suite as root. When we restore a VM snapshot VMWare creates fresh
        files which will subsequently be owned by root (if we are running as root). This will lead
        to the images being unopenable due to permissions issues. We fix the issue by chowning
        back the files. We could execute the vmrun commands in a separate non-root process but this
        is simpler.'''
        userid = tools_user()[0]
        for item in os.listdir(vmx_path):
            os.chown(os.path.join(vmx_path, item), userid, -1)

    def discover_device(self, discovery_keys):
        L.debug('Looking for device with keys {}'.format(discovery_keys))

        device = self._inventory_item_for_discovery_keys(discovery_keys)
        if device is None:
            return None

        device['output_directory'] = os.path.join(
            device['output_root'], self._context['run_directory'])

        # TODO: Make this more generic. It would be helpful to know what keys are required.
        # TODO: Consider making snapshots smarter. e.g. revert to LATEST snapshot with a specific
        # prefix.
        if 'vmx_path' not in device or 'vm_snapshot' not in device:
            raise XVEx("VMWare device inventory items need to specify: '{}' and '{}'".format(
                'vmx_path', 'vm_snapshot'))

        vmx_path = device['vmx_path']
        vm_snapshot = device['vm_snapshot']
        # Check that either the VM is stopped or we're already using it. I'm thinking ahead here to
        # potentially having tests running in parallel.
        state = VMWareDeviceDiscoverer._vm_state(vmx_path)
        if state == 'running' and vmx_path not in self._vms_in_use:
            raise XVEx(
                "The VM {} is currently in use by someone else (current state is '{}'')".format(
                    vmx_path, state))

        # Always add. It might already be there but we don't care
        self._vms_in_use.add(vmx_path)

        if state == 'running':
            VMWareDeviceDiscoverer._unpause_vm(vmx_path)
        else:
            L.debug("Reverting VM to snapshot: {}".format(vm_snapshot))
            VMWareDeviceDiscoverer._revert_vm_to_snapshot(vmx_path, vm_snapshot)
            VMWareDeviceDiscoverer._chown_vm_files(vmx_path)
            L.debug("Starting VM")
            VMWareDeviceDiscoverer._start_vm(vmx_path)

        VMWareDeviceDiscoverer._wait_for_vm_power(vmx_path)

        # It can take quite a while for IPs to become available.
        # TODO: Try to improve this. It seems like a VMWare issue. I can ping the machine well
        # before vmware reports its IPs
        timeup = TimeUp(60)
        ip = None
        while not timeup:
            try:
                L.debug('Waiting for VM IP to become available')
                ip = VMWareDeviceDiscoverer._get_vm_ip(vmx_path)
                break
            except XVProcessException as ex:
                if 'The VMware Tools are not running in the virtual machine' not in ex.stdout and \
                   'Unable to get the IP address' not in ex.stdout:
                    raise
                L.warning("Failed getting IP for VM: {}".format(ex))
                time.sleep(5)

        if ip is None:
            raise XVEx("Couldn't get IP for VM {}".format(vmx_path))

        connector = SimpleSSHConnector(
            ips=[ip],
            username=device['username'],
            ssh_key=device['ssh_key'],
            ssh_password=device['ssh_password'])

        return create_device(device['os_name'], device, connector)

    def release_devices(self):
        # TODO: Merge this into device teardown. Probably do it with a component, e.g. vm_manager.
        # However, we could do it via the connector and make it part of that objects responsibility.
        # The advantage with a component is that it's configurable, so we can configure things like
        # whether to update to a snapshot or whether to pause.
        for vmx in self._vms_in_use:
            L.debug("Pausing VM: {}".format(vmx))
            # VMWareDeviceDiscoverer._pause_vm(vmx)

    def cleanup(self):
        for vmx in self._vms_in_use:
            L.debug("Stopping VM: {}".format(vmx))
            # vmrun won't allow you to stop a paused VM. So we start then stop!
            VMWareDeviceDiscoverer._unpause_vm(vmx)
            VMWareDeviceDiscoverer._stop_vm(vmx)
