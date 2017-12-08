from xv_leak_tools.test_templating.templating import TemplateEvaluator, Replacee, Each

# Note that packet capture tests are inherently noisy at the moment. Very few (if any) VPN providers
# guarantee no non-tunnel traffic so false positives are almost guaranteed. The tests are still
# useful for investigatory purposes.

# This list will contain all the individual test configurations
TESTS = []

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
                    'name': 'generic',
                }
            },
        }
    ],
    'parameters': {
        # Check period here is quite long. The reason being that many VPN providers use an openvpn
        # settings called ping-timeout to decide if they lost contact with the VPN server. Often
        # that is set to 1 minute. We need to wait at least that long to see if there's a leak.
        'check_period': 90,
    }
}

TEMPLATE_PARAMETERS_LIST = [
    {
        'TEMPLATE': TEMPLATE,
        '$TEST_NAME': Each(
            [
                "TestDNSDisruptKillVPNProcess",
                "TestIPResponderDisruptKillVPNProcess",
                "TestPacketCaptureDisruptKillVPNProcess"
            ]),
    },
]

TESTS = TemplateEvaluator.generate(TEMPLATE_PARAMETERS_LIST)
