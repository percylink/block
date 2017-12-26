#!/usr/bin/env python
# Author(s): 'Percy Link' <percylink@gmail.com>
import copy
import unittest
from datetime import datetime

import pytz

from blokka.actors import Node, ACCEPTED, REJECTED
from blokka.entities import Chain, Transaction, Block
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

    def test_receive_chain_accept(self):
        n1 = None
        try:
            blk = {
                'timestamp': '2017-01-02T03:04:05.000123Z',
                'prev_hash': '1234',
                'data': {'foo': 'bar'}
            }
            dct = {
                'blocks': [blk]
            }
            chain = Chain.from_dict(dct)
            node_id = 'blah'
            backend = MockFileBackend(chains={node_id: chain})
            n1 = Node.start(node_id=node_id, backend=backend)
            p1 = n1.proxy()
            chain2 = copy.deepcopy(chain)
            blk2 = {
                'timestamp': '2017-01-02T03:04:05.000123Z',
                'prev_hash': Block.from_dict(blk).hash,
                'data': {'a': 'b'}
            }
            chain2.add_block(Block.from_dict(blk2))
            res = p1.receive_chain(chain2).get()
            self.assertEqual(res, ACCEPTED)
            self.assertEqual(p1.chain.get(), chain2)
        finally:
            n1.stop()

    def test_receive_chain_accept_same(self):
        n1 = None
        try:
            blk = {
                'timestamp': '2017-01-02T03:04:05.000123Z',
                'prev_hash': '1234',
                'data': {'foo': 'bar'}
            }
            dct = {
                'blocks': [blk]
            }
            chain = Chain.from_dict(dct)
            node_id = 'blah'
            backend = MockFileBackend(chains={node_id: chain})
            n1 = Node.start(node_id=node_id, backend=backend)
            p1 = n1.proxy()
            res = p1.receive_chain(chain).get()
            self.assertEqual(res, ACCEPTED)
            self.assertEqual(p1.chain.get(), chain)
        finally:
            n1.stop()

    def test_receive_chain_reject(self):
        n1 = None
        try:
            blk = {
                'timestamp': '2017-01-02T03:04:05.000123Z',
                'prev_hash': '1234',
                'data': {'foo': 'bar'}
            }
            blk2 = {
                'timestamp': '2017-01-02T03:04:05.000123Z',
                'prev_hash': Block.from_dict(blk).hash,
                'data': {'woo': 'hoo'}
            }
            dct = {
                'blocks': [blk, blk2]
            }
            chain = Chain.from_dict(dct)
            node_id = 'blah'
            backend = MockFileBackend(chains={node_id: chain})
            n1 = Node.start(node_id=node_id, backend=backend)
            p1 = n1.proxy()

            dct2 = {
                'blocks': [{
                    'timestamp': '2017-01-02T03:04:05.000123Z',
                    'prev_hash': 'abc',
                    'data': {'x': 'y'}
                }]
            }
            chain2 = Chain.from_dict(dct2)
            res = p1.receive_chain(chain2).get()
            self.assertEqual(res, REJECTED)
            self.assertEqual(p1.chain.get(), chain)
        finally:
            n1.stop()

    def test_receive_chain_reject_same_length_different_blocks(self):
        n1 = None
        try:
            blk = {
                'timestamp': '2017-01-02T03:04:05.000123Z',
                'prev_hash': '1234',
                'data': {'foo': 'bar'}
            }
            blk2 = {
                'timestamp': '2017-01-02T03:04:05.000123Z',
                'prev_hash': Block.from_dict(blk).hash,
                'data': {'woo': 'hoo'}
            }
            dct = {
                'blocks': [blk, blk2]
            }
            chain = Chain.from_dict(dct)
            node_id = 'blah'
            backend = MockFileBackend(chains={node_id: chain})
            n1 = Node.start(node_id=node_id, backend=backend)
            p1 = n1.proxy()

            blk3 = {
                'timestamp': '2017-01-02T03:04:05.000123Z',
                'prev_hash': Block.from_dict(blk).hash,
                'data': {'p': 'b'}
            }
            dct2 = {
                'blocks': [blk, blk3]
            }
            chain2 = Chain.from_dict(dct2)
            res = p1.receive_chain(chain2).get()
            self.assertEqual(res, REJECTED)
            self.assertEqual(p1.chain.get(), chain)
        finally:
            n1.stop()

    def test_share_chain_accepted(self):
        try:
            blk = {
                'timestamp': '2017-01-02T03:04:05.000123Z',
                'prev_hash': '1234',
                'data': {'foo': 'bar'}
            }
            blk2 = {
                'timestamp': '2017-01-02T03:04:05.000123Z',
                'prev_hash': Block.from_dict(blk).hash,
                'data': {'woo': 'hoo'}
            }
            dct = {
                'blocks': [blk, blk2]
            }
            chain = Chain.from_dict(dct)
            node_id = 'blah'
            backend = MockFileBackend(chains={node_id: chain})
            n1 = Node.start(node_id=node_id, backend=backend)
            p1 = n1.proxy()

            short_chain = Chain.from_dict({'blocks': [blk]})
            n2 = Node.start(node_id='2', backend=MockFileBackend({'2': short_chain}))
            n3 = Node.start(node_id='3', backend=MockFileBackend({'3': chain}))
            blk3 = {
                'timestamp': '2017-01-02T03:04:05.000123Z',
                'prev_hash': Block.from_dict(blk).hash,
                'data': {'p': 'b'}
            }
            dct2 = {
                'blocks': [blk, blk3]
            }
            chain2 = Chain.from_dict(dct2)
            n4 = Node.start(node_id='4', backend=MockFileBackend({'4': chain2}))
            p2 = n2.proxy()
            p3 = n3.proxy()
            p4 = n4.proxy()
            p1.register_peer(p2)
            p1.register_peer(p3)
            p1.register_peer(p4)
            p1.share_chain().get()
            for p in [p1, p2, p3]:
                self.assertEqual(p.chain.get(), chain)
            self.assertEqual(p4.chain.get(), chain2)
        finally:
            n1.stop()
            n2.stop()
            n3.stop()
            n4.stop()

    def test_share_chain_rejected(self):
        try:
            blk = {
                'timestamp': '2017-01-02T03:04:05.000123Z',
                'prev_hash': '1234',
                'data': {'foo': 'bar'}
            }
            blk2 = {
                'timestamp': '2017-01-02T03:04:05.000123Z',
                'prev_hash': Block.from_dict(blk).hash,
                'data': {'woo': 'hoo'}
            }
            dct = {
                'blocks': [blk, blk2]
            }
            chain = Chain.from_dict(dct)
            node_id = 'blah'
            backend = MockFileBackend(chains={node_id: chain})
            n1 = Node.start(node_id=node_id, backend=backend)
            p1 = n1.proxy()

            short_chain = Chain.from_dict({'blocks': [blk]})
            blk3 = {
                'timestamp': '2017-01-02T03:04:05.000123Z',
                'prev_hash': Block.from_dict(blk).hash,
                'data': {'p': 'b'}
            }
            dct2 = {
                'blocks': [blk, blk3]
            }
            chain2 = Chain.from_dict(dct2)
            n2 = Node.start(node_id='2', backend=MockFileBackend({'2': short_chain}))
            n3 = Node.start(node_id='3', backend=MockFileBackend({'3': chain2}))
            n4 = Node.start(node_id='4', backend=MockFileBackend({'4': chain2}))
            p2 = n2.proxy()
            p3 = n3.proxy()
            p4 = n4.proxy()
            p1.register_peer(p2)
            p1.register_peer(p3)
            p1.register_peer(p4)
            p1.share_chain().get()
            self.assertEqual(p1.chain.get(), short_chain)
            self.assertEqual(p2.chain.get(), short_chain)
            self.assertEqual(p3.chain.get(), chain2)
            self.assertEqual(p4.chain.get(), chain2)
        finally:
            n1.stop()
            n2.stop()
            n3.stop()
            n4.stop()
