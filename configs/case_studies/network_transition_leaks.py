from xv_leak_tools.helpers import current_os
from xv_leak_tools.test_templating.templating import TemplateEvaluator, Replacee, Each

# TODO: Add variants of the test which explicitly require local and public DNS servers.
# TODO: Ensure the tests check for number of adapters (they will fail, but checking is nicer)

# Note that packet capture tests are inherently noisy at the moment. Very few (if any) VPN providers
# guarantee no non-tunnel traffic so false positives are almost guaranteed. The tests are still
# useful for investigatory purposes.

# This list will contain all the individual test configurations
TESTS = []

if current_os() == "macos":
    TEST_NAMES = [
        "TestMacOSDNSDisruptEnableNewService",
        "TestMacOSDNSDisruptInterface",
        "TestMacOSDNSDisruptService",
        "TestMacOSDNSDisruptWifiPower",
        "TestMacOSIPResponderDisruptEnableNewService",
        "TestMacOSIPResponderDisruptInterface",
        "TestMacOSIPResponderDisruptService",
        "TestMacOSIPResponderDisruptWifiPower",
        "TestMacOSPacketCaptureDisruptEnableNewService",
        "TestMacOSPacketCaptureDisruptInterface",
        "TestMacOSPacketCaptureDisruptService",
        "TestMacOSPacketCaptureDisruptWifiPower",
    ]
elif current_os() == "windows":
    TEST_NAMES = [
        "TestWindowsDNSDisruptEnableNewAdapter",
        "TestWindowsDNSDisruptAdapter",
        "TestWindowsDNSDisruptWifiPower",
        "TestWindowsIPResponderDisruptEnableNewAdapter",
        "TestWindowsIPResponderDisruptAdapter",
        "TestWindowsIPResponderDisruptWifiPower",
        "TestWindowsPacketCaptureDisruptEnableNewAdapter",
        "TestWindowsPacketCaptureDisruptAdapter",
        "TestWindowsPacketCaptureDisruptWifiPower",
    ]
elif current_os() == "linux":
    TEST_NAMES = [
        # TODO: Need to add IP responder and packet capture tests for linux
        "TestLinuxDNSDisruptEnableNewService",
        "TestLinuxDNSDisruptInterface",
        "TestLinuxDNSDisruptService",
    ]

TEMPLATE = {
    "name": Replacee("$TEST_NAME"),
    "devices": [
        {
            "discovery_keys": {
                "device_id": "localhost"
            },
            "device_name": "localhost",
            "components": {
                "vpn_application": {
                    "name": "generic",
                }
            },
        }
    ],
    "parameters": {
        # Check period here is quite long here as it takes some providers a while to notice
        # disruptions and often they don't leak until they notice and try to do something about it.
        "check_period": 90,
    }
}

_TEMPLATE_PARAMETERS_LIST = [
    {
        "TEMPLATE": TEMPLATE,
        "$TEST_NAME": Each(TEST_NAMES),
    },
]

TESTS += TemplateEvaluator.generate(_TEMPLATE_PARAMETERS_LIST)
