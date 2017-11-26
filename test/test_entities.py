#!/usr/bin/env python
# Author(s): 'Percy Link' <percylink@gmail.com>
import json
import unittest

from entities import Block


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
        self.fail()
