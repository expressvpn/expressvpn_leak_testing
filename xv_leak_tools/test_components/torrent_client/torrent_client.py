import time
from collections import namedtuple
from xv_leak_tools.log import L
from xv_leak_tools.exception import XVEx
from xv_leak_tools.process import XVProcessException
from xv_leak_tools.test_components.component import Component

class Transmission(Component):

    def __init__(self, device, config):
        super().__init__(device, config)
        self.added_torrents = []
        self._daemon_started = False

    def __del__(self):
        self.close()

    def open(self):
        L.debug("Starting Transmission daemon")
        self._device.connector().execute(['transmission-daemon'])
        self._daemon_started = True

    def close(self):
        if self._daemon_started:
            L.debug("Stopping Transmission daemon")
            self.remove_added_torrents()
            pids = self._device.pgrep("transmission")
            for pid in pids:
                self._device.kill_process(pid)

    @staticmethod
    def _object_from_magnet_uri(magnet_uri):
        torrent = namedtuple('Torrent', ['xt', 'tr', 'dn'])
        if 'xt=urn:btih:' in magnet_uri:
            # This assumes there's only one xt per magnet URI.
            exact_topic = magnet_uri.split('xt=urn:btih:')[1].split('&')[0]
        else:
            raise XVEx('Cannot parse magnet URI; no (unique?) hash')

        tracker, display_name = None, None
        if 'tr=' in magnet_uri:
            tracker = magnet_uri.split('tr=')[1].split('&')[0]
        if 'dn=' in magnet_uri:
            display_name = magnet_uri.split('dn=')[1].split('&')[0]

        return torrent(exact_topic, tracker, display_name)

    def add_torrent(self, magnet_uri):
        if not self._daemon_started:
            L.debug("Transmission daemon not started; starting...")
            self.open()
            # TODO: replace this sleep with a timeout.
            time.sleep(1)
        L.debug("Adding {} to Transmission".format(magnet_uri))
        cmd = ['transmission-remote', '--add', "{}".format(magnet_uri)]
        out = self._device.connector().execute(cmd)
        if out[0]:
            raise XVProcessException(cmd, *out)

        self.added_torrents.append(self._object_from_magnet_uri(magnet_uri))

    def remove_torrent(self, torrent_id):
        if not self._daemon_started:
            self.open()
        L.debug("Removing {} from Transmission".format(torrent_id))
        cmd = ['transmission-remote', '-t', torrent_id, '--remove-and-delete']
        self._device.connector().execute(cmd)

    def remove_all_torrents(self):
        if not self._daemon_started:
            self.open()
        cmd = ['transmission-remote', '-t', 'all', '--remove-and-delete']
        self._device.connector().execute(cmd)

    def remove_added_torrents(self):
        if not self._daemon_started:
            self.open()
        for torrent in self.added_torrents:
            self.remove_torrent(torrent.xt)
            self.added_torrents.remove(torrent)

class TorrentClient(Component):

    def __init__(self, device, config):
        super().__init__(device, config)
        self.client = None

    def set_client(self, client):
        if client == 'transmission':
            self.client = Transmission(self._device, self._config)
        else:
            raise XVEx("{} is not a supported torrent client".format(client))

    def open(self):
        self.client.open()

    def close(self):
        self.client.close()

    def add_torrent(self, torrent):
        self.client.add_torrent(torrent)

    def remove_torrent(self, torrent):
        self.client.remove_torrent(torrent)

    def remove_all_torrents(self):
        self.client.remove_all_torrents()
