from xv_leak_tools.factory import Builder
from xv_leak_tools.test_components.torrent_client.torrent_client import TorrentClient

class TorrentClientBuilder(Builder):

    @staticmethod
    def name():
        return 'torrent_client'

    def build(self, device, config):
        return TorrentClient(device, config)
