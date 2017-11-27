#!/usr/bin/env python
# Author(s): 'Percy Link' <percylink@gmail.com>
import abc
import json
import os

from blokka.entities import Chain


class ChainBackend(object):

    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def save_chain(self, chain, node_id):
        pass

    @abc.abstractmethod
    def load_chain(self, node_id):
        pass


class FileBackend(ChainBackend):

    FILE_DIR = './tmp'

    def __init__(self):
        if not os.path.exists(self.FILE_DIR):
            os.mkdir(self.FILE_DIR)

    def __file_path(self, node_id):
        """
        :type node_id: str
        :rtype: str
        """
        return os.path.join(self.FILE_DIR, node_id + '.json')

    def save_chain(self, chain, node_id):
        """
        :type chain: blokka.entities.Chain
        :type node_id: str
        """
        json.dump(chain.to_dict(), open(self.__file_path(node_id), 'w'))

    def load_chain(self, node_id):
        """
        :type node_id: str
        :rtype: blokka.entities.Chain
        """
        dct = json.load(open(self.__file_path(node_id), 'r'))
        return Chain.from_dict(dct)
