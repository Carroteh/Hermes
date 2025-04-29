from importlib.util import source_hash

import pytest
import logging

from unittest.mock import AsyncMock, MagicMock


from hermes.kademlia.Contact import Contact
from hermes.kademlia.DHT import DHT
from hermes.kademlia.KBucket import KBucket
from hermes.kademlia.BucketList import BucketList
from hermes.kademlia.Protocol import Protocol
from hermes.kademlia.Router import Router
from hermes.kademlia.Support import K_VAL
from hermes.kademlia.Node import Node
from hermes.kademlia.Storage import Storage

logging.basicConfig(level=logging.INFO)

def test_kbucket_full():
    k = KBucket()
    for i in range(K_VAL):
        k.add_contact(Contact(None, i, 'host', 1))

    with pytest.raises(Exception):
        k.add_contact(Contact(None, K_VAL+1, 'host', 1))

def test_force_fail_add():
    contact = Contact(None, 1, 'host', 1)
    node = Node(contact, Storage())
    BucketList = node.bucket_list

@pytest.mark.asyncio
async def test_duplicate_id():
    dummy_contact = Contact(None, 0, 'host', 1)
    node = Node(dummy_contact, Storage())

    bucket_list = BucketList(5)
    #await bucket_list.add_contact(dummy_contact)
    await bucket_list.add_contact(Contact(None, 1, 'host', 1))
    await bucket_list.add_contact(Contact(None, 1, 'host', 1))

    #no split shouldve happened
    assert len(bucket_list.buckets) == 1
    # bucket should have one contact
    assert len(bucket_list.buckets[0].contacts) == 1

@pytest.mark.asyncio
async def test_split():
    dummy_contact = Contact(None, 0, 'host', 1)
    node = Node(dummy_contact, Storage())

    bucket_list = BucketList(5)

    # Add 1 more contact than K value, this should cause a split
    for i in range(0, K_VAL):
        await bucket_list.add_contact(Contact(None, i, 'host', 1))
    await bucket_list.add_contact(Contact(None, K_VAL+1, 'host', 1))

    assert len(bucket_list.buckets) > 1



