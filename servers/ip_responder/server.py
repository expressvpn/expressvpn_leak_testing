#!/usr/bin/env python3

import socket
import time
from collections import namedtuple

class Sink:

    TOKEN_LENGTH = 16

    def __init__(self, port=10000):
        self.known_clients = {}
        self.token_count = {}
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(("", port))

    def count_for_token(self, token):
        token = token[:self.TOKEN_LENGTH]
        return self.token_count.get(token, 0)

    def add_client(self, client):
        if len(client.token) >= self.TOKEN_LENGTH:
            token = client.token[:self.TOKEN_LENGTH]
            if token not in self.known_clients:
                self.token_count[token] = 0
                self.known_clients[token] = set([client.ip])
            else:
                self.known_clients[token].update([client.ip])
            self.token_count[token] += 1

    def is_query(self, client):
        return len(client.token) == self.TOKEN_LENGTH + 1 and client.token[-1] == 63

    def listen(self):
        print("Listening on %s:%s" % self.sock.getsockname())

        while True:
            data, address = self.sock.recvfrom(1024)
            client = namedtuple("Client", ["token", "ip", "port"])(data, *address)
            if self.is_query(client):
                print("Received {} from {}:{} QUERY".format(data, *address))
                self.respond(client)
            else:
                self.add_client(client)
                print("Received {} from {}:{}, token count = {}".format(
                    data, *address, self.count_for_token(client.token)))

    def respond(self, client):
        """
        This sends the list of IPs the client has connected from to the last IP
        the client has connected from, if the client passes a token matching
        client.token + b"?".
        """
        ips = bytes(" ".join(self.known_clients.get(client.token[:-1], set())), "ascii")
        # We sleep here because the client is (probably) synchronous.
        time.sleep(0.1)
        self.sock.sendto(ips, (client.ip, client.port))
        print("Sent {} to {}:{}".format(ips, client.ip, client.port))

if __name__ == "__main__":
    Sink().listen()
