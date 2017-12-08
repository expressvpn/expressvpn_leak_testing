from xv_leak_tools.test_components.cleanup.cleanup_vpns import CleanupVPNs

class WindowsCleanup(CleanupVPNs):

    # You can add more applications, processes etc. here or you can override this class
    # and the vpn_application component to avoid editing this one.

    VPN_PROCESS_NAMES = [
        'openvpn'
    ]

    VPN_APPLICATIONS = [
        'ExpressVPN.exe',
    ]

    UNKILLABLE_APPLICATIONS = []

    def __init__(self, device, config):
        super().__init__(
            device, config,
            WindowsCleanup.VPN_PROCESS_NAMES, WindowsCleanup.VPN_APPLICATIONS,
            WindowsCleanup.UNKILLABLE_APPLICATIONS)
