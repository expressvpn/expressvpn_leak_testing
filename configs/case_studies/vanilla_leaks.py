from xv_leak_tools.test_templating.templating import TemplateEvaluator, Replacee, Each

# This list will contain all the individual test configurations
TESTS = []

# Very simple template for the vanilla tests. There are no parameters or component specific
# configurations here.
TEMPLATE = {
    'name': Replacee("$NAME"),
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
}

TEMPLATE_PARAMETERS_LIST = [
    {
        'TEMPLATE': TEMPLATE,
        '$NAME': Each([
            'TestDNSVanilla',
            'TestDNSVanillaAggressive',
            'TestPublicIPAddress',
            'TestDNSVanillaAggressivePacketCapture',
            'TestIPResponderVanilla']),
    },
]

TESTS += TemplateEvaluator.generate(TEMPLATE_PARAMETERS_LIST)
