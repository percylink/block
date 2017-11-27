#!/usr/bin/env python
# Author(s): 'Percy Link' <percylink@gmail.com>
import abc
import json
from datetime import datetime

DATEFORMAT = '%Y-%m-%dT%H:%M:%S.%fZ'


class JSONSerializable(object):

    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def to_dict(self):
        pass

    @classmethod
    def from_dict(cls, dct):
        raise NotImplementedError

    def to_json(self):
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, jstr):
        return cls.from_dict(json.loads(jstr))


class Block(JSONSerializable):

    def __init__(self, index, timestamp, prev_hash, hash, data):
        """
        :type index: str
        :type timestamp: datetime.datetime
        :type prev_hash: str
        :type hash: str
        :type data: dict
        """
        self.index = index
        self.timestamp = timestamp
        self.prev_hash = prev_hash
        self.hash = hash
        self.data = data

    def to_dict(self):
        return {
            'index': self.index,
            'timestamp': self.timestamp.strftime(DATEFORMAT),
            'prev_hash': self.prev_hash,
            'hash': self.hash,
            'data': self.data
        }

    @classmethod
    def from_dict(cls, dct):
        return cls(
            index=dct['index'],
            timestamp=datetime.strptime(dct['timestamp'], DATEFORMAT),
            prev_hash=dct['prev_hash'],
            hash=dct['hash'],
            data=dct['data']
        )


class Chain(JSONSerializable):

    def __init__(self, blocks):
        """
        :type blocks: list[Block]
        """
        self.blocks = blocks

    def to_dict(self):
        return {
            "blocks": [b.to_dict() for b in self.blocks]
        }

    @classmethod
    def from_dict(cls, dct):
        return cls(
            blocks=[Block.from_dict(b) for b in dct['blocks']]
        )

    def add_block(self, block):
        """
        Add a block to the end of the chain
        :type block: Block
        """
        if len(self.blocks) > 0 and block.prev_hash != self.blocks[-1].hash:
            raise ValueError("New block's prev_hash must match the hash of the current "
                             "last block in the chain")
        self.blocks.append(block)

    def latest_hash(self):
        """
        Return the hash of the last block in the chain, or None if the chain has no blocks
        :rtype: str
        """
        if len(self.blocks) == 0:
            return None
        else:
            return self.blocks[-1].hash
