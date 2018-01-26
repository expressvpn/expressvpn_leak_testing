from xv_leak_tools.test_templating.templating import TemplateEvaluator, Replacee, Each

NO_IPV6 = False

STRONGEST_SETTINGS = """Ensure Network Lock, IPv6 leak protection and Only user ExpressVPN DNS
servers are enabled. Also ensure access to LAN is allowed"""

WEBRTC_TEMPLATE = {
    'name': "TestWebRTCICE",
    "devices": [
        {
            "discovery_keys": {
                "device_id": "localhost"
            },
            "device_name": "localhost",
            'components': {
                'vpn_application': {
                    'name': 'express_vpn',
                    'settings': {
                        'human_readable': STRONGEST_SETTINGS,
                    },
                },
            },
        },
    ],
    'parameters': {
        'browser': Replacee('$BROWSER'),
        'ask_perms': True,
    }
}

BROWSERS = [
    'chrome',
    'firefox',
    'opera',
    'safari',
]

TEMPLATE_PARAMETERS_LIST = [
    {
        'TEMPLATE': WEBRTC_TEMPLATE,
        '$BROWSER': Each(BROWSERS),
    },
]

if NO_IPV6:
    TESTS = []
else:
    TESTS = TemplateEvaluator.generate(TEMPLATE_PARAMETERS_LIST)

TEMPLATE = {
    'name': Replacee("$TEST_NAME"),
    'devices': [
        {
            "discovery_keys": {
                "device_id": "localhost"
            },
            "device_name": "localhost",
            'components': {
                'vpn_application': {
                    'name': 'express_vpn',
                    'settings': {
                        'human_readable': STRONGEST_SETTINGS,
                    }
                },
                'ip_responder': {
                    'ip_responder_server': '172.104.166.149',
                },
            },
        }
    ],
    'parameters': {
        'browser': 'firefox',
    }
}

TEMPLATE_PARAMETERS_LIST = [
    {
        'TEMPLATE': TEMPLATE,
        '$TEST_NAME': Each([

            # Vanilla tests
            'TestDNSVanilla',
            'TestDNSVanillaAggressive',
            'TestPublicIPAddress',
            'TestIPResponderVanilla',

            # DNS Tests
            'TestMacOSDNSDisruptEnableNewService',
            'TestMacOSDNSForcePublicDNSServers',
            'TestMacOSDNSDisruptInterface',
            'TestMacOSDNSDisruptReorderServices',
            'TestMacOSDNSDisruptService',
            'TestMacOSDNSDisruptWifiPower',
            'TestDNSDisruptKillVPNProcess',
            'TestDNSDisruptVPNConnection',

            # IP Responder Tests
            'TestMacOSIPResponderDisruptEnableNewService',
            'TestMacOSIPResponderDisruptInterface',
            'TestMacOSIPResponderDisruptReorderServices',
            'TestMacOSIPResponderDisruptService',
            'TestMacOSIPResponderDisruptWifiPower',
            'TestIPResponderDisruptKillVPNProcess',
            'TestIPResponderDisruptVPNConnection',

            # Manual Tests
            # Disable to keep the tests automated - move manual tests to different config
            # 'TestDNSDisruptCable',
            # 'TestIPResponderDisruptCable',
        ]),
    },
]

TESTS += TemplateEvaluator.generate(TEMPLATE_PARAMETERS_LIST)
