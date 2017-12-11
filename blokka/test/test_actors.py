#!/usr/bin/env python
# Author(s): 'Percy Link' <percylink@gmail.com>
import unittest
from datetime import datetime

import pytz

from blokka.actors import Node
from blokka.entities import Chain, Transaction
from blokka.test import MockFileBackend


class TestNode(unittest.TestCase):

    def test_chain(self):
        node = None
        try:
            node_id = 'aaa'
            blk = {
                'timestamp': '2017-01-02T03:04:05.000123Z',
                'prev_hash': '1234',
                'data': {'foo': 'bar'}
            }
            dct = {
                'blocks': [blk]
            }
            chain = Chain.from_dict(dct)
            backend = MockFileBackend(chains={node_id: chain})
            node = Node.start(node_id=node_id, backend=backend)
            proxy = node.proxy()
            self.assertEqual(proxy.chain.get(), chain)
        finally:
            node.stop()

    def test_register_peer(self):
        n1 = None
        n2 = None
        try:
            n1 = Node.start(node_id='1')
            p1 = n1.proxy()
            n2 = Node.start(node_id='2')
            p2 = n2.proxy()
            p1.register_peer(p2)
            self.assertEqual(p1.peer_proxies.get(), [p2])
        finally:
            n1.stop()
            n2.stop()

    def test_register_and_share_transaction(self):
        n1 = None
        n2 = None
        try:
            n1 = Node.start(node_id='1')
            p1 = n1.proxy()
            n2 = Node.start(node_id='2')
            p2 = n2.proxy()
            p1.register_peer(p2)

            t = Transaction(
                seller_id='s',
                buyer_id='b',
                timestamp=datetime(2017, 11, 1, 1, 2, 3, tzinfo=pytz.UTC),
                amount=32.1
            )
            p1.register_transaction(t)
            self.assertEqual(p1.pending_transactions.get(), {t.hash: t})
            self.assertEqual(p2.pending_transactions.get(), {t.hash: t})
        finally:
            n1.stop()
            n2.stop()

    def test_should_mine(self):
        n1 = None
        try:
            n1 = Node.start(node_id='1')
            p1 = n1.proxy()
            p1.pending_transactions = {i: i for i in xrange(Node.BLOCK_SIZE - 1)}
            self.assertFalse(p1.should_mine().get())
            p1.pending_transactions = {i: i for i in xrange(Node.BLOCK_SIZE)}
            self.assertTrue(p1.should_mine().get())
        finally:
            n1.stop()

    def test_receive_chain(self):
        self.fail()

    def test_share_chain_accepted(self):
        self.fail()

    def test_share_chain_rejected(self):
        self.fail()