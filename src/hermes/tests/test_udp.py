import random

import pytest
import logging

import asyncio


from hermes.kademlia.Contact import Contact
from hermes.kademlia.DHT import DHT
from hermes.kademlia.KBucket import KBucket
from hermes.kademlia.BucketList import BucketList
from hermes.kademlia.Protocol import Protocol
from hermes.kademlia.Router import Router
from hermes.kademlia.Support import K_VAL
from hermes.kademlia.Node import Node
from hermes.kademlia.Storage import Storage
from hermes.net.UDPProtocol import UDPProtocol
from hermes.net.UDPServer import UDPServer

logging.basicConfig(level=logging.INFO)

@pytest.mark.asyncio
async def test_store_route():
    p1 = UDPProtocol("127.0.0.1", 2720)
    id1 = random.randint(0, 2**160-1)
    c1 = Contact(p1, id1, host="127.0.0.1", port=2720)
    n1 = Node(c1, Storage())
    server1 = UDPServer(n1, "127.0.0.1", 2720)
    server1_task = asyncio.create_task(server1.start())

    p2 = UDPProtocol("127.0.0.1", 2721)
    c2 = Contact(p2, random.randint(0, 2 ** 160 - 1), host="127.0.0.1", port=2721)
    n2 = Node(c2, Storage())
    server2 = UDPServer(n2, "127.0.0.1", 2721)
    server2_task = asyncio.create_task(server2.start())

    sender = Contact(p1, id1, host="127.0.0.1", port=2720)
    test_id = random.randint(0, 2**160-1)
    test_value = "Test"

    error = await p2.store(sender, test_id, test_value, 360000)
    assert not error.has_error()
    assert n2.storage.contains(test_id)
    assert n2.storage.get(test_id) == test_value

    await server1.stop()
    await server2.stop()
    server1_task.cancel()
    server2_task.cancel()

@pytest.mark.asyncio
async def test_unresponsive_store_node():
    # Node 1 (responsive)
    p1 = UDPProtocol("127.0.0.1", 2720)
    c1 = Contact(p1, random.randint(0, 2**160 - 1), host="127.0.0.1", port=2720)
    n1 = Node(c1, Storage())
    server1 = UDPServer(n1, "127.0.0.1", 2720)
    server_task1 = asyncio.create_task(server1.start())

    # Node 2 (unresponsive)
    p2 = UDPProtocol("127.0.0.1", 2721)
    c2 = Contact(p2, random.randint(0, 2**160 - 1), host="127.0.0.1", port=2721)
    n2 = Node(c2, Storage())
    server2 = UDPServer(n2, "127.0.0.1", 2721)
   # server_task2 = asyncio.create_task(server2.start())

    # Test store to unresponsive node
    sender = Contact(p1, random.randint(0, 2**160 - 1), host="127.0.0.1", port=2720)
    test_id = random.randint(0, 2**160 - 1)
    test_value = "Test"
    error = await p2.store(sender, test_id, test_value, 3600)
    assert error.timeout_error

    # Cleanup
    await server1.stop()
    await server2.stop()
    server_task1.cancel()
   # server_task2.cancel()

@pytest.mark.asyncio
async def test_find_node_route():
    # Node 1
    p1 = UDPProtocol("127.0.0.1", 2720)
    id1 = random.randint(0, 2 ** 160 - 1)
    c1 = Contact(p1, id1, host="127.0.0.1", port=2720)
    n1 = Node(c1, Storage())
    server1 = UDPServer(n1, "127.0.0.1", 2720)
    server1_task = asyncio.create_task(server1.start())

    # Node 2
    p2 = UDPProtocol("127.0.0.1", 2721)
    id2 = random.randint(0, 2 ** 160 - 1)
    c2 = Contact(p2, id2, host="127.0.0.1", port=2721)
    n2 = Node(c2, Storage())
    server2 = UDPServer(n2, "127.0.0.1", 2721)
    server2_task = asyncio.create_task(server2.start())

    # Test find_node RPC
    sender = Contact(p1, id1, host="127.0.0.1", port=2720)
    target_key = random.randint(0, 2 ** 160 - 1)

    contacts, error = await p2.find_node(sender, target_key)
    assert not error.has_error()
    assert isinstance(contacts, list)

    # Cleanup
    await server1.stop()
    await server2.stop()
    server1_task.cancel()
    server2_task.cancel()

@pytest.mark.asyncio
async def test_unresponsive_find_node():
    # Node 1 (responsive)
    p1 = UDPProtocol("127.0.0.1", 2720)
    id1 = random.randint(0, 2 ** 160 - 1)
    c1 = Contact(p1, id1, host="127.0.0.1", port=2720)
    n1 = Node(c1, Storage())
    server1 = UDPServer(n1, "127.0.0.1", 2720)
    server1_task = asyncio.create_task(server1.start())

    # Node 2 (unresponsive)
    p2 = UDPProtocol("127.0.0.1", 2721)
    id2 = random.randint(0, 2 ** 160 - 1)
    c2 = Contact(p2, id2, host="127.0.0.1", port=2721)

    # Test find_node to unresponsive node
    sender = Contact(p1, id1, host="127.0.0.1", port=2720)
    target_key = random.randint(0, 2 ** 160 - 1)

    contacts, error = await p2.find_node(sender, target_key)
    assert error.timeout_error

    # Cleanup
    await server1.stop()
    server1_task.cancel()

@pytest.mark.asyncio
async def test_find_value_route():
    # Node 1
    p1 = UDPProtocol("127.0.0.1", 2720)
    id1 = random.randint(0, 2 ** 160 - 1)
    c1 = Contact(p1, id1, host="127.0.0.1", port=2720)
    n1 = Node(c1, Storage())
    server1 = UDPServer(n1, "127.0.0.1", 2720)
    server1_task = asyncio.create_task(server1.start())

    # Node 2
    p2 = UDPProtocol("127.0.0.1", 2721)
    id2 = random.randint(0, 2 ** 160 - 1)
    c2 = Contact(p2, id2, host="127.0.0.1", port=2721)
    n2 = Node(c2, Storage())
    server2 = UDPServer(n2, "127.0.0.1", 2721)
    server2_task = asyncio.create_task(server2.start())

    # Store value on Node 2
    test_key = random.randint(0, 2 ** 160 - 1)
    test_value = "Test Value"
    n2.storage.set(test_key, test_value)

    # Test find_value RPC
    sender = Contact(p1, id1, host="127.0.0.1", port=2720)
    contacts, value, error = await p2.find_value(sender, test_key)

    assert not error.has_error()
    assert value == test_value

    # Cleanup
    await server1.stop()
    await server2.stop()
    server1_task.cancel()
    server2_task.cancel()

@pytest.mark.asyncio
async def test_unresponsive_find_value():
    # Node 1 (responsive)
    p1 = UDPProtocol("127.0.0.1", 2720)
    id1 = random.randint(0, 2 ** 160 - 1)
    c1 = Contact(p1, id1, host="127.0.0.1", port=2720)
    n1 = Node(c1, Storage())
    server1 = UDPServer(n1, "127.0.0.1", 2720)
    server1_task = asyncio.create_task(server1.start())

    # Node 2 (unresponsive)
    p2 = UDPProtocol("127.0.0.1", 2721)
    id2 = random.randint(0, 2 ** 160 - 1)
    c2 = Contact(p2, id2, host="127.0.0.1", port=2721)

    # Test find_value to unresponsive node
    sender = Contact(p1, id1, host="127.0.0.1", port=2720)
    test_key = random.randint(0, 2 ** 160 - 1)

    value, error = await p2.find_value(sender, test_key)
    assert error.timeout_error

    # Cleanup
    await server1.stop()
    server1_task.cancel()

@pytest.mark.asyncio
async def test_ping_route():
    # Node 1
    p1 = UDPProtocol("127.0.0.1", 2720)
    id1 = random.randint(0, 2 ** 160 - 1)
    c1 = Contact(p1, id1, host="127.0.0.1", port=2720)
    n1 = Node(c1, Storage())
    server1 = UDPServer(n1, "127.0.0.1", 2720)
    server1_task = asyncio.create_task(server1.start())

    # Node 2
    p2 = UDPProtocol("127.0.0.1", 2721)
    id2 = random.randint(0, 2 ** 160 - 1)
    c2 = Contact(p2, id2, host="127.0.0.1", port=2721)
    n2 = Node(c2, Storage())
    server2 = UDPServer(n2, "127.0.0.1", 2721)
    server2_task = asyncio.create_task(server2.start())

    # Test ping RPC
    sender = Contact(p1, id1, host="127.0.0.1", port=2720)
    error = await p2.ping(sender)

    assert not error.has_error()

    # Cleanup
    await server1.stop()
    await server2.stop()
    server1_task.cancel()
    server2_task.cancel()

@pytest.mark.asyncio
async def test_unresponsive_ping():
    # Node 1 (responsive)
    p1 = UDPProtocol("127.0.0.1", 2720)
    id1 = random.randint(0, 2 ** 160 - 1)
    c1 = Contact(p1, id1, host="127.0.0.1", port=2720)
    n1 = Node(c1, Storage())
    server1 = UDPServer(n1, "127.0.0.1", 2720)
    server1_task = asyncio.create_task(server1.start())

    # Node 2 (unresponsive)
    p2 = UDPProtocol("127.0.0.1", 2721)
    id2 = random.randint(0, 2 ** 160 - 1)
    c2 = Contact(p2, id2, host="127.0.0.1", port=2721)

    # Test ping to unresponsive node
    sender = Contact(p1, id1, host="127.0.0.1", port=2720)
    error = await p2.ping(sender)

    assert error.timeout_error

    # Cleanup
    await server1.stop()
    server1_task.cancel()