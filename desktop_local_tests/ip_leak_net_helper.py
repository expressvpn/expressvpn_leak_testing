import ipaddress
import time

from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from xv_leak_tools.helpers import TimeUp
from xv_leak_tools.log import L
from xv_leak_tools.test_framework.assertions import Assertions

class IPLeakNetHelper(Assertions):

    URL = 'https://ipleak.net'

    def __init__(self, webdriver):
        self._webdriver = webdriver

    @staticmethod
    def _parse_potential_ips(potential_ips):
        ips = []
        for potential_ip in potential_ips:
            try:
                potential_ip = ipaddress.ip_address(potential_ip)
                ips.append(potential_ip)
            except ValueError as _:
                continue
        return ips

    def _activate_torrent_leak_detection(self):
        # TODO: Use wrapper and do wait_for_element_by_id()
        torrent_detection_refresh = self._webdriver.find_element_by_id('torrent_detection_refresh')
        torrent_detection_refresh.click()

    def load_page(self):
        self._webdriver.get(IPLeakNetHelper.URL)

    def get_magnet_link(self, timeout=10):
        self._activate_torrent_leak_detection()
        # Add a loop to wait for the page to load the piece we want
        # TODO: This might be a good helper function. A wrapper to "wait for element"
        magnet_link = None
        timeup = TimeUp(timeout)
        while not timeup:
            try:
                magnet_link = (
                    self._webdriver.find_element_by_id('torrent_detection')
                    .find_element_by_tag_name('div')
                    .find_element_by_tag_name('a')
                    .get_attribute('href')
                )
                break
            except NoSuchElementException as _:
                time.sleep(0.5)

        self.assertIsNotNone(magnet_link, "Torrent detection div didn't load")
        return magnet_link

    def get_reported_torrent_ips(self):
        try:
            anchors = (
                self._webdriver.find_element_by_id('torrent_detection')
                .find_element_by_class_name('docs_verbose')
                .find_elements_by_tag_name('a')
            )

            for anchor in anchors:
                # Refresh the reported IPs
                if anchor.text == 'Refresh':
                    anchor.click()

            potential_ips = []
            table_cells = (
                self._webdriver.find_element_by_id('torrent_detection')
                .find_elements_by_tag_name('td')
            )

            for cell in table_cells:
                for atag in cell.find_elements_by_tag_name('a'):
                    potential_ips.append(atag.text)
                for btag in cell.find_elements_by_tag_name('b'):
                    potential_ips.append(btag.text)

            return IPLeakNetHelper._parse_potential_ips(potential_ips)

        except StaleElementReferenceException as _:
            # Likely this means that just as we were inspecting the page the page updated itself
            # The site continuously updated reported torrent IPs so there's a small chance this
            # can happen. We can live with it.
            L.warning(
                "ipleak.net updated it's torrent IPs whilst we were reading them. Couldn't "
                "determine any IPs this time.")

            return []
        except NoSuchElementException as ex:
            self.failTest("Couldn't parse the web page contents to get torrent IPs: {}".format(ex))
