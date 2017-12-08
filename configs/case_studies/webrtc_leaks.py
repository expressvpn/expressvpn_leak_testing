from xv_leak_tools.helpers import current_os
from xv_leak_tools.test_templating.templating import TemplateEvaluator, Replacee, Each

# This list will contain all the individual test configurations
TESTS = []

# Template for the vanilla test. This test doesn't ask the user for any specific browser
# permissions. If an app fails this test then it is persistently leaking IP addresses to any
# webpage which asks for the IPs.
TEMPLATE_VANILLA = {
    'name': "TestWebRTCICE",
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
        'browser': Replacee('$BROWSER'),
    }
}

TEMPLATE_PERMISSIONS_GRANTED = {
    'name': "TestWebRTCICE",
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
        'browser': Replacee('$BROWSER'),
        'ask_perms': True,
    }
}

# Run the tests on all major browsers for the current OS.
BROWSERS = ['chrome', 'opera', 'firefox']

if current_os() == 'macos':
    BROWSERS.append('safari')
elif current_os() == 'windows':
    BROWSERS.append('edge')

# Duplicate the test templates for each browser
TESTS += TemplateEvaluator.generate([{'TEMPLATE': TEMPLATE_VANILLA, '$BROWSER': Each(BROWSERS)}])
TESTS += TemplateEvaluator.generate(
    [{'TEMPLATE': TEMPLATE_PERMISSIONS_GRANTED, '$BROWSER': Each(BROWSERS)}])
