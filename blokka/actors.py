#!/usr/bin/env python
# Author(s): 'Percy Link' <percylink@gmail.com>
import json
import logging

import sys
from collections import Counter
from datetime import datetime

import pytz
from pykka import ThreadingActor

from blokka.backends import FileBackend
from blokka.entities import Block


def build_logger(name):
    handler = logging.StreamHandler(stream=sys.stdout)
    formatter = logging.Formatter(
        '%(asctime)-20s - %(name)-10s - %(levelname)-10s - %(message)s'
    )
    handler.setFormatter(formatter)
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    return logger


ACCEPTED = 'accepted'
REJECTED = 'rejected'


class Node(ThreadingActor):

    BLOCK_SIZE = 5
    REJECTION_THRESH_FRAC = 0.5

    def __init__(self, node_id, backend=None):
        super(Node, self).__init__()
        self.node_id = node_id
        self.peer_proxies = []
        self.chain_backend = backend or FileBackend()
        self.pending_transactions = {}

        self.logger = build_logger(':'.join([self.__class__.__name__, self.node_id]))

    @property
    def chain(self):
        return self.chain_backend.load_chain(self.node_id)

    def register_peer(self, peer_proxy):
        """

        :type peer_proxy:
        :rtype:
        """
        self.logger.debug('registering peer: {}'.format(peer_proxy.node_id.get()))
        self.peer_proxies.append(peer_proxy)

    def register_transaction(self, transaction):
        """
        :type transaction: blokka.entities.Transaction
        """
        # First check if it's already in the dict - if not, add to pending transactions
        # and share with peers
        if transaction.hash not in self.pending_transactions:
            self.logger.debug('adding transaction {} to pending transactions'
                              .format(transaction.to_dict()))
            self.pending_transactions[transaction.hash] = transaction
            self.share_transaction(transaction)
        else:
            self.logger.debug('transaction {} already in pending transactions'
                              .format(transaction.to_dict()))

        # Mine a block, if it's time
        if self.should_mine():
            self.mine_block()

    def share_transaction(self, transaction):
        """
        :type transaction: blokka.entities.Transaction
        """
        for peer in self.peer_proxies:
            peer.register_transaction(transaction)

    def should_mine(self):
        """

        :rtype: bool
        """
        return len(self.pending_transactions) >= self.BLOCK_SIZE

    def mine_block(self):
        self.logger.debug('mining now')
        t = pytz.UTC.localize(datetime.utcnow())
        data = json.dumps(
            {k: v.to_dict() for k, v in self.pending_transactions.iteritems()})
        new_block = Block(
            timestamp=t,
            prev_hash=self.chain.latest_hash(),
            data=data)
        self.chain.add_block(new_block)
        self.share_chain()

    def share_chain(self):
        responses = []
        for peer in self.peer_proxies:
            response = peer.receive_chain(self.chain).get()
            responses.append(response)
        counts = Counter(responses)
        if float(len(counts[REJECTED])) / len(responses) > self.REJECTION_THRESH_FRAC:
            self.chain
            # Keep a count of fraction of peers who accept vs reject
            # If rejected by more than allowed fraction, remove the last block

    def receive_chain(self, chain):
        if chain.length > self.chain.length:
            self.chain_backend.save_chain(chain, self.node_id)
            return ACCEPTED
        else:
            return REJECTED


# new transaction created on one node
# this node shares it with peers, then adds it to its transaction list and checks if it should mine a block
# if so, it builds a block (method complexity TBD) and adds it to the chain
# it then shares the chain with peers
# when receiving a transaction, follow the same steps
# when receiving a chain, compare the contents and the length - if the same, do nothing;
# if not, choose the longer one... if the same length, do what? and how to not lose
# whatever pending_transactions were in the discarded block? - somehow parse which ones are not in a block and keep those
