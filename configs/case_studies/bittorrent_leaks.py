from xv_leak_tools.test_templating.templating import TemplateEvaluator, Replacee, Each

# This list will contain all the individual test configurations
TESTS = []

TEMPLATE = {
    'name': "TestTorrentTrackerIPLeakNet",
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
        # Change this if you don't use chrome as your default browser. It doesn't really matter
        # which one you use here.
        'browser': 'chrome',
        # It's known that some torrent clients cache your IP addresses. For the purpose of this test
        # let's exclude that because it would pollute results. Caching is a separate issue.
        # If torrent_client_preopened is True then ALL VPN providers are going to leak here.
        'torrent_client_preopened': False,
        'torrent_client': Replacee("$TORRENT_CLIENT"),
    }
}

# Currently we only test transmission and utorrent. You can extend the tests to cover any
# client by creating a torrent client class and adding it to the list below.
TEMPLATE_PARAMETERS_LIST = [
    {
        'TEMPLATE': TEMPLATE,
        '$TORRENT_CLIENT': Each(['transmission', 'utorrent']),
    },
]

TESTS += TemplateEvaluator.generate(TEMPLATE_PARAMETERS_LIST)
