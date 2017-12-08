from xv_leak_tools.test_components.cleanup.cleanup_vpns import CleanupVPNs

class MacOSCleanup(CleanupVPNs):

    # You can add more applications, processes etc. here or you can override this class
    # and the vpn_application component to avoid editing this one.

    VPN_PROCESS_NAMES = [
        'openvpn',
        'racoon',
        'pppd',
    ]

    VPN_APPLICATIONS = [
        '/Applications/ExpressVPN.app/Contents/MacOS/ExpressVPN',
    ]

    UNKILLABLE_APPLICATIONS = []

    def __init__(self, device, config):
        super().__init__(
            device, config,
            MacOSCleanup.VPN_PROCESS_NAMES, MacOSCleanup.VPN_APPLICATIONS,
            MacOSCleanup.UNKILLABLE_APPLICATIONS)
