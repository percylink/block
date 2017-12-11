#!/usr/bin/env python
# Author(s): 'Percy Link' <percylink@gmail.com>
import abc
import json
from datetime import datetime
from hashlib import sha256

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


class ObjectEqualMixin(object):

    def __eq__(self, other):
        return isinstance(other, self.__class__) and other.__dict__ == self.__dict__

    def __ne__(self, other):
        return not self == other


class BaseEntity(JSONSerializable, ObjectEqualMixin):
    pass


class Transaction(BaseEntity):

    def __init__(self, seller_id, buyer_id, timestamp, amount):
        self.seller_id = seller_id
        self.buyer_id = buyer_id
        self.timestamp = timestamp
        self.amount = amount

    @property
    def hash(self):
        return sha256(self.to_json()).hexdigest()

    def to_dict(self):
        return {
            'seller_id': self.seller_id,
            'buyer_id': self.buyer_id,
            'timestamp': self.timestamp.strftime(DATEFORMAT),
            'amount': self.amount
        }

    @classmethod
    def from_dict(cls, dct):
        return cls(
            seller_id=dct['seller_id'],
            buyer_id=dct['buyer_id'],
            timestamp=datetime.strptime(dct['timestamp'], DATEFORMAT),
            amount=dct['amount']
        )


class Block(BaseEntity):

    def __init__(self, timestamp, prev_hash, data):
        """
        :type timestamp: datetime.datetime
        :type prev_hash: str
        :type data: dict
        """
        self.timestamp = timestamp
        self.prev_hash = prev_hash
        self.data = data

        self.hash = self.__make_hash()

    def __make_hash(self):
        raw = [self.timestamp.strftime(DATEFORMAT), self.prev_hash, self.data]
        return sha256(json.dumps(raw)).hexdigest()

    def to_dict(self):
        return {
            'timestamp': self.timestamp.strftime(DATEFORMAT),
            'prev_hash': self.prev_hash,
            'hash': self.hash,
            'data': self.data
        }

    @classmethod
    def from_dict(cls, dct):
        return cls(
            timestamp=datetime.strptime(dct['timestamp'], DATEFORMAT),
            prev_hash=dct['prev_hash'],
            data=dct['data']
        )


class Chain(BaseEntity):

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

    def remove_latest_block(self):
        """
        Remove last block in the chain
        """
        if len(self.blocks) > 0:
            self.blocks = self.blocks[:-1]

    def latest_hash(self):
        """
        Return the hash of the last block in the chain, or None if the chain has no blocks
        :rtype: str
        """
        if len(self.blocks) == 0:
            return None
        else:
            return self.blocks[-1].hash

    @property
    def length(self):
        return len(self.blocks)
