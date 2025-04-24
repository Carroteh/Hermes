import random

import pytest
import logging

from unittest.mock import AsyncMock, MagicMock


from hermes.core.Contact import Contact
from hermes.core.DHT import DHT
from hermes.core.KBucket import KBucket
from hermes.core.BucketList import BucketList
from hermes.core.Protocol import Protocol
from hermes.core.Router import Router
from hermes.core.Support import K_VAL
from hermes.core.Node import Node
from hermes.core.Storage import Storage

logging.basicConfig(level=logging.INFO)

@pytest.mark.asyncio
async def test_bootstrap_outside_bootstrapping_bucket():
    # 32 virtual protocols, 1 for bootstrap peer, 20 for bootstrap peer friends
    # 10 for nodes one of those nodes knows about, and one for us

    # new node ends up knowing of 11 contacts, since the bootstrap protocol finds other peers
    # not in the same bucket as the known peer

    vps : list[Protocol] = []

    for i in range(32):
        vps.append(Protocol())

    # US
    randid = random.randint(0, 2**160)
    dht_us: DHT = DHT(randid, vps[0], Storage(), Router(Node(Contact(vps[0], randid, 'host', 1), Storage())))
    vps[0].node = dht_us.router.node

    # BOOTSTRAP NODE DHT
    randid = random.randint(0, 2 ** 158)
    dht_bootstrap: DHT = DHT(randid, vps[1], Storage(), Router(Node(Contact(vps[1], randid, 'host', 1), Storage())))
    vps[1].node = dht_bootstrap.router.node

    n = None
    for i in range(20):
        if i < 19:
            randid = random.randint(0, 2 ** 158)
        else:
            randid = 2**160

        c = Contact(vps[i+2], randid, 'host', 1)
        n = Node(c, Storage())
        vps[i+2].node = n
        await dht_bootstrap.router.node.bucket_list.add_contact(c)


    # one other node knows about 10 other contacts
    for i in range(10):
        randid = random.randint(0, 2 ** 160)
        c = Contact(vps[i+22], randid, 'host', 1)
        n2 = Node(c, Storage())
        vps[i+22].node = n
        await n.bucket_list.add_contact(c)

    await dht_us.bootstrap(dht_bootstrap.router.node.our_contact)

    contacts = [c for b in dht_us.router.node.bucket_list.buckets for c in b.contacts]
    assert len(contacts) == 31

@pytest.mark.asyncio
async def test_bootstrap_within_bootstrapping_bucket():
    # 22 virtual protocols, 1 for bootstrap peer, 10 for bootstrap peer friends
    # 10 for nodes one of those nodes knows about, and one for us

    # new node ends up knowing of 11 contacts, since the bootstrap protocol finds other peers
    # not in the same bucket as the known peer

    vps : list[Protocol] = []

    for i in range(22):
        vps.append(Protocol())

    # US
    randid = random.randint(0, 2**160)
    dht_us: DHT = DHT(randid, vps[0], Storage(), Router(Node(Contact(vps[0], randid, 'host', 1), Storage())))
    vps[0].node = dht_us.router.node

    # BOOTSTRAP NODE DHT
    randid = random.randint(0, 2 ** 160)
    dht_bootstrap: DHT = DHT(randid, vps[1], Storage(), Router(Node(Contact(vps[1], randid, 'host', 1), Storage())))
    vps[1].node = dht_bootstrap.router.node

    n = None

    for i in range(10):
        randid = random.randint(0, 2 ** 160)
        c = Contact(vps[i+2], randid, 'host', 1)
        n = Node(c, Storage())
        vps[i+2].node = n
        await dht_bootstrap.router.node.bucket_list.add_contact(c)


    # one other node knows about 10 other contacts
    for i in range(10):
        randid = random.randint(0, 2 ** 160)
        c = Contact(vps[i+12], randid, 'host', 1)
        n2 = Node(c, Storage())
        vps[i+12].node = n
        await n.bucket_list.add_contact(c)

    await dht_us.bootstrap(dht_bootstrap.router.node.our_contact)

    contacts = [c for b in dht_us.router.node.bucket_list.buckets for c in b.contacts]
    assert len(contacts) == 11