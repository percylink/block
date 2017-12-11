#!/usr/bin/env python
# Author(s): 'Percy Link' <percylink@gmail.com>
import json
import unittest

from blokka.entities import Block, Chain, Transaction


class TestBlock(unittest.TestCase):

    def test_from_dict_to_dict(self):
        dct = {
            'timestamp': '2017-01-02T03:04:05.000123Z',
            'prev_hash': '1234',
            'data': {'foo': 'bar'}
        }
        b = Block.from_dict(dct)
        dct['hash'] = b.hash
        self.assertEqual(b.to_dict(), dct)

    def test_json(self):
        dct = {
            'timestamp': '2017-01-02T03:04:05.000123Z',
            'prev_hash': '1234',
            'data': {'foo': 'bar'}
        }
        b = Block.from_json(json.dumps(dct))
        dct['hash'] = b.hash
        self.maxDiff = None
        self.assertEqual(json.loads(b.to_json()), dct)


class TestChain(unittest.TestCase):

    def test_from_dict_to_dict(self):
        blk = {
            'timestamp': '2017-01-02T03:04:05.000123Z',
            'prev_hash': '1234',
            'data': {'foo': 'bar'}
        }
        dct = {
            'blocks': [blk]
        }
        chain = Chain.from_dict(dct)
        dct['blocks'][-1]['hash'] = chain.blocks[-1].hash
        self.assertEqual(chain.to_dict(), dct)

    def test_add_block(self):
        blk = {
            'timestamp': '2017-01-02T03:04:05.000123Z',
            'prev_hash': '1234',
            'data': {'foo': 'bar'}
        }
        dct = {
            'blocks': [blk]
        }
        chain = Chain.from_dict(dct)
        b2 = {
            'timestamp': '2017-01-02T03:04:05.000123Z',
            'prev_hash': Block.from_dict(blk).hash,
            'data': {'on': 'point'}
        }
        chain.add_block(Block.from_dict(b2))
        self.assertEqual(
            chain.to_dict(),
            {'blocks': [Block.from_dict(blk).to_dict(), Block.from_dict(b2).to_dict()]}
        )

        # prev_hash doesn't match last hash - should fail
        b3 = {
            'timestamp': '2017-01-02T03:04:05.000123Z',
            'prev_hash': Block.from_dict(blk).hash,
            'data': {'some': 'thing'}
        }
        self.assertRaises(ValueError, chain.add_block, Block.from_dict(b3))

    def test_latest_hash(self):
        block_dicts = [
            {
                'timestamp': '2017-01-02T03:04:05.000123Z',
                'prev_hash': '1234',
                'data': {'foo': 'bar'}
            },
            {
                'timestamp': '2017-01-02T03:04:05.000123Z',
                'prev_hash': '5678',
                'data': {'on': 'point'}
            }
        ]
        chain = Chain.from_dict(
            {'blocks': block_dicts}
        )
        self.assertEqual(chain.latest_hash(), Block.from_dict(block_dicts[-1]).hash)
        chain2 = Chain(blocks=[])
        self.assertIsNone(chain2.latest_hash())


class TestTransaction(unittest.TestCase):

    def test_from_dict_to_dict(self):
        d = {
            'seller_id': 'a',
            'buyer_id': 'b',
            'timestamp': '2017-12-25T00:00:00.000000Z',
            'amount': 4.5
        }
        t = Transaction.from_dict(d)
        self.assertEqual(t.to_dict(), d)