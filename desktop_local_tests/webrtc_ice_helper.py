import ipaddress
import json
import os
import time

from xv_leak_tools.exception import XVEx
from xv_leak_tools.log import L
from xv_leak_tools.manual_input import message_and_await_enter
from xv_leak_tools.path import windows_real_path

class WebRTCICEHelper: # pylint: disable=too-few-public-methods

    TIME_TO_WAIT_FOR_IPS = 2

    def __init__(self, localhost, webdriver, ask_perms=False, host_remotely=False):
        self._localhost = localhost
        self._webdriver = webdriver
        self._ask_perms = ask_perms
        self._host_remotely = host_remotely

    def _start_server(self):
        root_folder = os.path.join(os.path.dirname(__file__), 'support', 'ice_lookup')
        if self._host_remotely:
            # TODO: Don't hardcode port
            return self._localhost['webserver'].start_server(root_folder, 6666, https=True)

        # If we're using cygwin then the browser won't be able to find the file unless we convert
        # to the real windows path. This is safe to call on other OSes
        return "file://{}".format(windows_real_path(os.path.abspath(root_folder)))

    def _stop_server(self):
        if self._host_remotely:
            self._localhost['webserver'].stop_server()

    def _url(self, url_base):
        html_file = 'ice_lookup_ask_perms.html' if self._ask_perms else 'ice_lookup_no_perms.html'
        # If we're using cygwin then the browser won't be able to find the file unless we convert
        # to the real windows path. This is safe to call on other OSes
        return os.path.join(url_base, html_file)

    def _webrtc_ips(self, url_base):
        url = self._url(url_base)
        L.describe("Open ICE detection webpage {}".format(url))
        self._webdriver.get(url)

        # TODO: This isn't working properly. Also, try to automate
        if self._ask_perms:
            message_and_await_enter("Please grant the browser permissions to use audio/video")

        # Not in love with this but not sure we have a lot of choice. There's no way to know whether
        # the javascript code has done searching for IPs TODO: Verify that
        L.describe("Wait for {} seconds for IPs to report".format(
            WebRTCICEHelper.TIME_TO_WAIT_FOR_IPS))
        time.sleep(WebRTCICEHelper.TIME_TO_WAIT_FOR_IPS)

        if 'xv_leak_tools local ICE IP detection' not in self._webdriver.title:
            raise XVEx("Got unexpected webpage title: {}".format(self._webdriver.title))

        L.describe("Check ICE detection webpage doesn't show our public IP addresses")
        inner_html = self._webdriver.find_element_by_id('ice_ips').get_attribute('innerHTML')
        if not inner_html:
            raise XVEx('ice_ips div in webrtc page contained no inner_html')
        json_reponse = json.loads(inner_html)

        if not json_reponse['webrtc_supported']:
            L.warning('WebRTC not supported for this browser. Reporting no ips.')
            return []

        return [ipaddress.ip_address(ip) for ip in json_reponse['ips']]

    def webrtc_ips(self):
        # In absence of RAII we have to do this. TODO: If we end up with lots of specialised
        # webdriver logic or have to repeat this in multiple places then we may need to rethink
        # this. Need a clean way to share code.
        try:
            return self._webrtc_ips(self._start_server())
        except:
            raise
        finally:
            self._stop_server()
            # Firefox needs a quit on macos else it hangs :(
            self._webdriver.quit()
