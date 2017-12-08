# pylint: skip-file

CONTEXT = {
    'output_directory': None,
    'run_directory': None,
    'log_level': 'INFO',
    'allow_manual': True,
    'stop_on_fail': False,
    'running_in_ci': False,
    'package_paths': [],
    'test_packages': [
        'desktop_local_tests',
        'generic_tests',
        'multimachine_tests',
        'xv_leak_tools.test_framework',
    ],
    'component_packages': [
        'xv_leak_tools.test_components.cleanup',
        'xv_leak_tools.test_components.dns_tool',
        'xv_leak_tools.test_components.firewall',
        'xv_leak_tools.test_components.git',
        'xv_leak_tools.test_components.ip_responder',
        'xv_leak_tools.test_components.ip_tool',
        'xv_leak_tools.test_components.network_configuration',
        'xv_leak_tools.test_components.network_tool',
        'xv_leak_tools.test_components.open_wrt',
        'xv_leak_tools.test_components.packet_capturer',
        'xv_leak_tools.test_components.route',
        'xv_leak_tools.test_components.settings',
        'xv_leak_tools.test_components.vpn_application',
        'xv_leak_tools.test_components.webdriver',
        'xv_leak_tools.test_components.webserver',
    ],
    'default_device_components':
    {
        'cleanup': {},
    }
}
