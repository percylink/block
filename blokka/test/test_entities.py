#!/usr/bin/env python
# Author(s): 'Percy Link' <percylink@gmail.com>
import json
import unittest

from blokka.entities import Block, Chain


class TestBlock(unittest.TestCase):

    def test_from_dict_to_dict(self):
        dct = {
            'index': '1',
            'timestamp': '2017-01-02T03:04:05.000123Z',
            'prev_hash': '1234',
            'hash': '5678',
            'data': {'foo': 'bar'}
        }
        b = Block.from_dict(dct)
        self.assertEqual(b.to_dict(), dct)

    def test_json(self):
        dct = {
            'index': '1',
            'timestamp': '2017-01-02T03:04:05.000123Z',
            'prev_hash': '1234',
            'hash': '5678',
            'data': {'foo': 'bar'}
        }
        b = Block.from_json(json.dumps(dct))
        self.assertEqual(b.to_json(), json.dumps(dct))


class TestChain(unittest.TestCase):

    def test_from_dict_to_dict(self):
        blk = {
            'index': '1',
            'timestamp': '2017-01-02T03:04:05.000123Z',
            'prev_hash': '1234',
            'hash': '5678',
            'data': {'foo': 'bar'}
        }
        dct = {
            'blocks': [blk]
        }
        chain = Chain.from_dict(dct)
        self.assertEqual(chain.to_dict(), dct)

    def test_add_block(self):
        blk = {
            'index': '1',
            'timestamp': '2017-01-02T03:04:05.000123Z',
            'prev_hash': '1234',
            'hash': '5678',
            'data': {'foo': 'bar'}
        }
        dct = {
            'blocks': [blk]
        }
        chain = Chain.from_dict(dct)
        b2 = {
            'index': '2',
            'timestamp': '2017-01-02T03:04:05.000123Z',
            'prev_hash': '5678',
            'hash': 'abcd',
            'data': {'on': 'point'}
        }
        chain.add_block(Block.from_dict(b2))
        self.assertEqual(
            chain.to_dict(),
            {'blocks': [
                {
                    'index': '1',
                    'timestamp': '2017-01-02T03:04:05.000123Z',
                    'prev_hash': '1234',
                    'hash': '5678',
                    'data': {'foo': 'bar'}
                },
                {
                    'index': '2',
                    'timestamp': '2017-01-02T03:04:05.000123Z',
                    'prev_hash': '5678',
                    'hash': 'abcd',
                    'data': {'on': 'point'}
                }
            ]}
        )

        # prev_hash doesn't match last hash - should fail
        b3 = {
            'index': '3',
            'timestamp': '2017-01-02T03:04:05.000123Z',
            'prev_hash': '5678',
            'hash': '3333',
            'data': {'some': 'thing'}
        }
        self.assertRaises(ValueError, chain.add_block, Block.from_dict(b3))

    def test_latest_hash(self):
        chain = Chain.from_dict(
            {'blocks': [
                {
                    'index': '1',
                    'timestamp': '2017-01-02T03:04:05.000123Z',
                    'prev_hash': '1234',
                    'hash': '5678',
                    'data': {'foo': 'bar'}
                },
                {
                    'index': '2',
                    'timestamp': '2017-01-02T03:04:05.000123Z',
                    'prev_hash': '5678',
                    'hash': 'abcd',
                    'data': {'on': 'point'}
                }
            ]}
        )
        self.assertEqual(chain.latest_hash(), 'abcd')
        chain2 = Chain(blocks=[])
        self.assertIsNone(chain2.latest_hash())
