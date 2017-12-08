from xv_leak_tools.test_components.torrent_client.torrent_client_builder import TorrentClientBuilder

def register(factory):
    factory.register(TorrentClientBuilder())
