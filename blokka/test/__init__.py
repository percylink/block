#!/usr/bin/env python
# Author(s): 'Percy Link' <percylink@gmail.com>


class MockFileBackend(object):

    def __init__(self, chains):
        self.saved = {}
        self.chains = chains

    def save_chain(self, chain, node_id):
        self.saved[node_id] = chain
        self.chains[node_id] = chain

    def load_chain(self, node_id):
        return self.chains.get(node_id)
