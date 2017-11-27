#!/usr/bin/env python
# Author(s): 'Percy Link' <percylink@gmail.com>
import unittest

from blokka.actors import Node


class TestNode(unittest.TestCase):

    def test_on_receive(self):
        n = Node.start(node_id='me')
        res = n.ask({'msg': 'hello world'})
        print res

        n.stop()