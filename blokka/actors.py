#!/usr/bin/env python
# Author(s): 'Percy Link' <percylink@gmail.com>
from pykka import ThreadingActor

from backends import FileBackend


class Node(ThreadingActor):

    def __init__(self, node_id, backend=None):
        super(Node, self).__init__()
        self.node_id = node_id
        self.peer_proxies = []
        self.chain_backend = backend or FileBackend()

    def on_receive(self, message):
        print(message)
        return 'foo'
