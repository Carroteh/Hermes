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

def test_kbucket_full():
    k = KBucket()
    for i in range(K_VAL):
        k.add_contact(Contact(None, i))

    with pytest.raises(Exception):
        k.add_contact(Contact(None, K_VAL+1))

def test_force_fail_add():
    contact = Contact(None, 1)
    node = Node(contact, Storage())
    BucketList = node.bucket_list

@pytest.mark.asyncio
async def test_duplicate_id():
    dummy_contact = Contact(None, 0)
    node = Node(dummy_contact, Storage())

    bucket_list = BucketList(5)
    #await bucket_list.add_contact(dummy_contact)
    await bucket_list.add_contact(Contact(None, 1))
    await bucket_list.add_contact(Contact(None, 1))

    #no split shouldve happened
    assert len(bucket_list.buckets) == 1
    # bucket should have one contact
    assert len(bucket_list.buckets[0].contacts) == 1

@pytest.mark.asyncio
async def test_split():
    dummy_contact = Contact(None, 0)
    node = Node(dummy_contact, Storage())

    bucket_list = BucketList(5)

    # Add 1 more contact than K value, this should cause a split
    for i in range(0, K_VAL):
        await bucket_list.add_contact(Contact(None, i))
    await bucket_list.add_contact(Contact(None, K_VAL+1))

    assert len(bucket_list.buckets) > 1

@pytest.mark.asyncio
async def test_lookup():
    """
    Test the lookup function in the Router class
    to ensure it resolves nodes correctly and handles edge cases.
    """
    # Setup: Create a Router instance and mock dependencies
    mock_node = MagicMock()  # Mocked Node instance
    mock_node.bucket_list.get_close_contacts = AsyncMock(return_value=[MagicMock(id=1001), MagicMock(id=1002)])

    router = Router(mock_node)

    # Mocking necessary methods
    router.rpc_find_nodes = AsyncMock(
        return_value=[MagicMock(id=2001), MagicMock(id=2002)]
    )
    router.get_closer_nodes = AsyncMock(
        return_value=[MagicMock(id=3001), MagicMock(id=3002)]
    )

    # Input key for lookup
    target_key = 1234

    # Act: Call the lookup method
    result = await router.lookup(target_key, router.rpc_find_nodes)

    # Assert: Check if the output matches the expected structure
    assert result is not None, "The result should not be None"
    assert len(result) > 0, "The result should contain at least one resolved node"
    assert all(hasattr(node, "id") for node in result), "Each node should have an 'id' attribute"

    # Verify interactions with mocked methods
    router.rpc_find_nodes.assert_called_with(target_key)
    router.get_closer_nodes.assert_called_with(target_key, [])

def test_local_store_found_value():
    vp = Protocol()
    dht = DHT(1, vp, Storage(), Router(Node(Contact(vp, 1), Storage())))
    key = 4
    val = "Test"
    dht.store(key, val)
    retval = dht.storage.get(key)
    assert retval == val

@pytest.mark.asyncio
async def test_value_stored_in_closer_node():
    vp1 = Protocol()
    vp2 = Protocol()

    store1 = Storage()
    store2 = Storage()

    # Ensure all nodes are closer since our ID is max
    dht = DHT(2**160, vp1, store1, Router(Node(Contact(vp1, 2**160), store1)))
    vp1.node = dht.router.node

    # Make a closer contact
    contact_id = 2**159
    other_contact = Contact(vp2, contact_id)
    other_node = Node(other_contact, store2)
    vp2.node = other_node

    #Add other contact to peer list
    await dht.router.node.bucket_list.add_contact(other_contact)

    ghost_contact = Contact(Protocol(), 777)
    key = 0
    val = "Test"

    # Store a key-value pair in other node
    other_node.store(ghost_contact, key, val, 1000000)

    assert not store1.contains(key)
    assert store2.contains(key)

    ok, ok, retval = await dht.find_value(key)

    assert retval == val

@pytest.mark.asyncio
async def test_value_stored_in_farther_node():
    vp1 = Protocol()
    vp2 = Protocol()

    store1 = Storage()
    store2 = Storage()

    # Ensure all nodes are farther since our ID is 0
    dht = DHT(0, vp1, store1, Router(Node(Contact(vp1, 0), store1)))
    vp1.node = dht.router.node

    # Make a contact
    contact_id = 1
    other_contact = Contact(vp2, contact_id)
    other_node = Node(other_contact, store2)
    vp2.node = other_node

    #Add other contact to peer list
    await dht.router.node.bucket_list.add_contact(other_contact)

    ghost_contact = Contact(Protocol(), 777)
    key = 0
    val = "Test"

    # Store a key-value pair in other node
    other_node.store(ghost_contact, key, val, 1000000)

    # Our peer does NOT have the key-value
    assert not store1.contains(key)

    # Other node should have the key-value
    assert store2.contains(key)

    ok, ok, retval = await dht.find_value(key)

    assert retval == val

@pytest.mark.asyncio
async def test_value_stored_gets_propagated():
    vp1 = Protocol()
    vp2 = Protocol()
    store1 = Storage()
    store2 = Storage()

    dht = DHT(2**160, vp1, store1, Router(Node(Contact(vp1, 2**160), store1)))
    vp1.node = dht.router.node

    # Make a contact
    contact_id = 2**159
    other_contact = Contact(vp2, contact_id)
    other_node = Node(other_contact, store2)
    vp2.node = other_node

    #Add other contact to peer list
    await dht.router.node.bucket_list.add_contact(other_contact)

    ghost_contact = Contact(Protocol(), 777)
    key = 0
    val = "Test"



    # Our peer does NOT have the key-value
    assert not store1.contains(key)
    # Other node should NOT have the key-value
    assert not store2.contains(key)

    # Store a key-value pair
    dht.store(key, val)

    # Now both nodes should have the stored key-value
    assert not store1.contains(key)
    assert not store2.contains(key)

