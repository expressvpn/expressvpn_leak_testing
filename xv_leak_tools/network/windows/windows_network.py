import ipaddress
import re
import sys

from xv_leak_tools.exception import XVEx
from xv_leak_tools.helpers import merge_two_dicts
from xv_leak_tools.log import L
from xv_leak_tools.path import windows_safe_path
from xv_leak_tools.process import XVProcessException, check_subprocess

_PROG_WINDUMP = re.compile(r"([\d]+)\.\\Device\\NPF_({[^}]+}) \(([^\)]+)\)")

# Credit to http://autosqa.com/blog/index.php/2016/03/18/how-to-parse-wmic-output-with-python/ for
# saving me writing this!
def parse_wmic_output(text):
    result = []
    # remove empty lines
    lines = [s for s in text.splitlines() if s.strip()]
    # No Instance(s) Available
    if len(lines) == 0:
        return result
    header_line = lines[0]
    # Find headers and their positions
    headers = re.findall(r'\S+\s+|\S$', header_line)
    pos = [0]
    for header in headers:
        pos.append(pos[-1] + len(header))
    for iheader, header in enumerate(headers):
        headers[iheader] = headers[iheader].strip()
    # Parse each entries
    for iline in range(1, len(lines)):
        row = {}
        for ipos in range(len(pos) - 1):
            row[headers[ipos]] = lines[iline][pos[ipos]:pos[ipos + 1]].strip()
        result.append(row)
    return result

def wmic_array_to_list(array):
    if array.strip() == "":
        return []
    quoted_strings = array.replace('{', '').replace('}', '').split(',')
    return [qs.replace('"', '').strip() for qs in quoted_strings]

def wmic_rows():
    rows = []
    nic_rows = parse_wmic_output(check_subprocess(['wmic', 'nic'])[0])
    nicconfig_rows = parse_wmic_output(check_subprocess(['wmic', 'nicconfig'])[0])
    # We're effectively performing a join on SettingID and GUID here.
    for nic_row in nic_rows:
        if nic_row['GUID'] == "":
            L.verbose("Network adapter '{}' has no GUID. Ignoring it!".format(nic_row['Name']))
            continue
        for nicconfig_row in nicconfig_rows:
            if nicconfig_row['SettingID'] == nic_row['GUID']:
                rows.append(merge_two_dicts(nic_row, nicconfig_row))
                break
    return rows

class WindowsAdapter:

    def __init__(self, wmic_data):
        self.data = wmic_data

    def __eq__(self, other):
        return self.guid() == other.guid()

    def __str__(self):
        return "{DeviceID}: {NetConnectionID} ({Name}, {GUID}) enabled = {NetEnabled} ".format(
            **self.data)

    def __repr__(self):
        return self.__str__()

    def pretty_string(self):
        return """\
DeviceID:           {DeviceID}
NetConnectionID:    {NetConnectionID}
Name:               {Name}
GUID:               {GUID}
IPConnectionMetric: {IPConnectionMetric}
DefaultIPGateway:   {DefaultIPGateway}
Windump Index:      {windump_index}
Enabled:            {NetEnabled}""".format(**self.data)

    def matches(self, key, value):
        if self.data[key].strip() == value.strip():
            return True
        return False

    def all_string(self):
        ret = ""
        maxlength = max(len(s) for s in list(self.data.keys()))
        format_string = "{:" + str(maxlength) + "}: {}\n"
        for key, value in list(self.data.items()):
            if value.strip() != "":
                ret += format_string.format(key, value)
        return ret

    def refresh(self):
        for row in wmic_rows():
            if row['GUID'] == self.guid():
                self.data = row
                return
        raise XVEx("Couldn't find adapter with GUID {} when refreshing data".format(
            self.guid()))

    def windump_index(self):
        return self.data['windump_index']

    def guid(self):
        return self.data['GUID']

    def device_id(self):
        return self.data['DeviceID']

    # In Network and Sharing Center->Adapter Settings this is the "Device Name"
    def name(self):
        return self.data['Name']

    # In Network and Sharing Center->Adapter Settings this is the "Name"
    def net_connection_id(self):
        return self.data['NetConnectionID']

    def enabled(self):
        return self.data['NetEnabled'] == "TRUE"

    def enable(self):
        if self.enabled():
            return
        try:
            check_subprocess(
                ['netsh', 'interface', 'set', 'interface', self.net_connection_id(), 'enabled'])
            self.data['NetEnabled'] = 'TRUE'
        except XVProcessException as ex:
            raise XVEx("Failed to enable interface {}: {}".format(self.net_connection_id(), ex))

    def disable(self):
        if not self.enabled():
            return
        try:
            check_subprocess(
                ['netsh', 'interface', 'set', 'interface', self.net_connection_id(), 'disabled'])
            self.data['NetEnabled'] = 'FALSE'
        except XVProcessException as ex:
            raise XVEx("Failed to disable interface {}: {}".format(self.net_connection_id(), ex))

    def dns_servers(self):
        return [ipaddress.ip_address(ip) for ip in wmic_array_to_list(
            self.data['DNSServerSearchOrder'])]

    def ip_addresses(self):
        return [ipaddress.ip_address(ip) for ip in wmic_array_to_list(self.data['IPAddress'])]

    def interface_metric(self):
        try:
            return int(self.data['IPConnectionMetric'])
        except ValueError:
            return sys.maxsize

    def set_interface_metric(self, value=0):
        cmd = [
            windows_safe_path("C:\\WINDOWS\\system32\\WindowsPowerShell\\v1.0\\powershell.exe"),
            "Set-NetIPInterface",
            "-InterfaceIndex",
            self.data['InterfaceIndex'],
            "-InterfaceMetric",
            str(value)
        ]
        check_subprocess(cmd)
        self.data['IPConnectionMetric'] = str(value)

    def pingable(self):
        if not self.enabled():
            L.verbose("{} not enabled".format(self.name()))
            return False
        ips = self.ip_addresses()
        if not ips:
            L.verbose("{} has no IP address".format(self.name()))
            return False
        cmd = ['ping', '-n', '1', '-w', '2', '-S', ips[0].exploded, '8.8.8.8']
        try:
            output = check_subprocess(cmd)[0]
            if 'Received = 1' in output:
                return True
            else:
                # Consider this a real error and propagate. It's likely a code issue.
                raise XVEx("Don't know how to parse ping output: {}".format(output))
        except XVProcessException as ex:
            if 'Lost = 1' in ex.stderr:
                L.debug("Couldn't ping on adapter {}".format(self))
                return False
            L.warning(
                "Ping failed unexpectedly with error '{}'. "
                "Assuming adapter {} un-pingable.".format(ex.stderr, self))

            return False

    def set_dns_servers(self, *ips):
        if len(ips) > 2:
            raise XVEx("There is only space for two DNS servers per adapter")
        cmd_set = ['netsh', 'interface', 'ip', 'set', 'dns', self.net_connection_id()]
        if not ips:
            cmd_set.append('dhcp')
            L.debug("Setting DNS on {} via DHCP".format(self.net_connection_id()))
            check_subprocess(cmd_set)
        else:
            # TODO: this breaks if we set a server that's already set. Not sure
            # if that's a problem.
            L.debug("Setting primary DNS on {} to {}".format(self.net_connection_id(), ips[0]))
            check_subprocess(cmd_set + ['static', ips[0], 'index=1'])
            if len(ips) == 2:
                cmd_add = ['netsh', 'interface', 'ip', 'add', 'dns', self.net_connection_id()]
                L.debug("Setting secondary DNS on {} to {}".format(
                    self.net_connection_id(), ips[1]))
                check_subprocess(cmd_add + [ips[1], 'index=2'])

class WindowsNetwork:

    @staticmethod
    def _windump_index(guid, windump_lines):
        # Try to parse something
        # 1.\Device\NPF_{0F888A67-F8CF-4B5E-8812-5473E4A1D365} (ExpressVPN Tap Adapter)
        for line in windump_lines:
            match = _PROG_WINDUMP.match(line)
            if not match:
                continue
            if match.group(2) == guid:
                return match.group(1)
        L.warning("Couldn't find windump interface index for adapter with GUID {}".format(guid))
        return "0"

    @staticmethod
    def _adapters_by(key, value, unique=True):
        adapters = [adapter for adapter in WindowsNetwork.adapters() if adapter.matches(key, value)]
        if unique and len(adapters) > 1:
            raise XVEx("More than one network adapter matched key {} => {}".format(key, value))
        return adapters

    @staticmethod
    def adapters():
        adapters = []
        # This is an optimization. Calling windump is slow. So we do it once to save waiting for
        # each adapter to do it.
        windump_lines = check_subprocess(['windump', '-D'])[0].splitlines()
        for row in wmic_rows():
            if row['PhysicalAdapter'] == "FALSE":
                continue
            row['windump_index'] = WindowsNetwork._windump_index(row['GUID'], windump_lines)
            adapters.append(WindowsAdapter(row))

        return adapters

    @staticmethod
    def adapters_in_priority_order():
        adapters = WindowsNetwork.adapters()
        adapters.sort(key=lambda adapter: adapter.interface_metric())
        return adapters

    @staticmethod
    def adapter_by_name(name):
        adapters = WindowsNetwork._adapters_by("Name", name, unique=True)
        if not adapters:
            raise XVEx("Couldn't find adapter with name '{}'".format(name))
        return adapters[0]

    @staticmethod
    def adapter_by_net_connection_id(id_):
        adapters = WindowsNetwork._adapters_by("NetConnectionID", id_, unique=True)
        if not adapters:
            raise XVEx("Couldn't find adapter with network connection ID '{}'".format(id_))
        return adapters[0]
