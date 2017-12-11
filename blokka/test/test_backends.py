#!/usr/bin/env python
# Author(s): 'Percy Link' <percylink@gmail.com>
import json
import shutil
import unittest
from datetime import datetime
import os

import pytz

from blokka.backends import FileBackend
from blokka.entities import Chain, Block


class TestFileBackend(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.backend = FileBackend()

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(FileBackend.FILE_DIR)

    def test_save_chain(self):
        chain = Chain(
            blocks=[Block(
                timestamp=datetime(2017, 8, 9, 10, 11, 12, tzinfo=pytz.UTC),
                prev_hash='abcd',
                data={'foo': 'bar'}
            )])
        self.backend.save_chain(chain, 'n1')
        d = json.load(open(os.path.join(FileBackend.FILE_DIR, 'n1.json')))
        self.assertEqual(d, chain.to_dict())

    def test_load_chain(self):
        chain = Chain(
            blocks=[Block(
                timestamp=datetime(2017, 8, 9, 10, 11, 12, tzinfo=pytz.UTC),
                prev_hash='xxyy',
                data={'foo': 'bar'}
            )])
        json.dump(chain.to_dict(), open(os.path.join(FileBackend.FILE_DIR, 'n2.json'), 'w'))
        c2 = self.backend.load_chain('n2')
        self.assertEqual(c2.to_dict(), chain.to_dict())
