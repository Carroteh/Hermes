import random

from hermes.kademlia.KBucket import KBucket
from hermes.kademlia.Protocol import Protocol
from hermes.kademlia.Contact import Contact
from hermes.kademlia.RPCError import RPCError
from hermes.kademlia.Storage import Storage
from hermes.kademlia.Router import Router
from hermes.kademlia.Node import Node
from hermes.net.UDPServer import UDPServer
from hermes.kademlia.Support import BUCKET_REFRESH_INTERVAL

import datetime

class DHT:
    def __init__(self, id: int, protocol: Protocol, storage: Storage, local_addr: tuple[str, int] = ('0.0.0.0', 3301)):
        self._storage: Storage = storage
        self._protocol:Protocol = protocol
        self._our_id: int = id
        self._our_contact: Contact = Contact(protocol, id, local_addr[0], local_addr[1])
        self._node: Node = Node(self._our_contact, storage)
        self._router: Router = Router(self._node)
        self._router.set_error_handler(self.handle_error)
        #UDP server
        self._server = UDPServer(self._node, self._our_contact.host, self._our_contact.port)

    def _set_addr_in_contact(self, addr: tuple[str, int]):
        self._our_contact.host = addr[0]
        self._our_contact.port = addr[1]
        self._server.port = addr[1]
        self._server.host = addr[0]

    async def start(self):
        await self._server.start(self._set_addr_in_contact)

    async def stop(self):
        await self._server.stop()

    async def store(self, key: int, val: str):
        """
        Store a key value pair on the DHT. (on K closer contacts
        """
        self._touch_bucket_with_key(key)
        self._storage.set(key, val)
        await self._store_on_closer_contacts(key, val)

    async def find_value(self, key: int) -> (bool, list[Contact], str):
        self._touch_bucket_with_key(key)

        our_val = None
        contacts_queried: list[Contact] = []

        # Return is Found, contacts, val
        ret = (False, None, None)

        if self._storage.contains(key):
            ret = (True, None, self._storage.get(key))
        else:
            found, contacts, found_by, val = await self._router.lookup(key, self.router.rpc_find_value)

            if found:
                ret = (True, None, val)

                # Cache the key in the node closest to the contact
                store_to_candidates = sorted([c for c in contacts if c != found_by], key=lambda c: c.id ^ key)

                if len(store_to_candidates) > 0:
                    store_to = store_to_candidates[0]
                    separating_nodes = self._get_separating_nodes_count(self._our_contact, store_to)
                    error = await store_to.protocol.store(self._node.our_contact, key, val, BUCKET_REFRESH_INTERVAL)
                    self.handle_error(error, store_to)
        return ret

    def _touch_bucket_with_key(self, key):
        pass

    async def _store_on_closer_contacts(self, key:  int, val: str) -> None:
        now: datetime = datetime.datetime.now()

        kbucket = self._node.bucket_list.get_kbucket(key)
        contacts = []

        if (now - kbucket.timestamp).total_seconds()*1000 < BUCKET_REFRESH_INTERVAL:
            contacts = await self._node.bucket_list.get_close_contacts(key, self._node.our_contact.id)
        else:
            found, contacts, found_by, val = await self.router.lookup(key, self._router.rpc_find_nodes)

        for c in list(contacts):
            error = await c.protocol.store(self._node.our_contact, key, val)
            self.handle_error(error, c)

    async def bootstrap(self, known_peer: Contact):
        """
        bootstrap our peer by contacting another, adding its contacts to our list, then getting the contacts
        for other peers not in the bucket range of our known peer we're joining.
        """
        error: RPCError
        contacts: list[Contact] = []

        # Add known peer to our contacts
        await self._node.bucket_list.add_contact(known_peer)
        # Send RPC to known peer to add ourselves to many peers and to get their information ourselves
        contacts, error = await known_peer.protocol.find_node(self._our_contact, self._our_id)
        self.handle_error(error, known_peer)

        if not error.has_error():
            for contact in list(contacts):
                # Add the returned peers to our contacts
                await self._node.bucket_list.add_contact(contact)


            # Refresh the other buckets (not containing the known peer bucket) to expand our network
            known_peer_bucket: KBucket = self._node.bucket_list.get_kbucket(known_peer.id)
            other_buckets = [b for b in self._node.bucket_list.buckets if b != known_peer_bucket]

            for other_bucket in other_buckets:
                await self._refresh_bucket(other_bucket)

        return error

    async def _refresh_bucket(self, bucket: KBucket):
        """
        do an RPC for a random ID in the bucket to discover more peers
        """
        bucket.touch()
        # Pick a random ID to query
        rand_id = self._random_id_in_bucket(bucket)
        contacts: list[Contact] = list(bucket.contacts)

        for contact in list(contacts):
            # Discover more peers
            (new_contacts, timeout_error) = await contact.protocol.find_node(self._our_contact, rand_id)
            self.handle_error(timeout_error, contact)
            for nc in list(new_contacts):
                # Add new peers
                await self._node.bucket_list.add_contact(nc)

    def _random_id_in_bucket(self, bucket: KBucket):
        return random.randint(bucket.low, bucket.high)

    def _get_separating_nodes_count(self, contact1, contact2):
        return 0

    def handle_error(self, error: RPCError, contact: Contact):
        pass

    @property
    def protocol(self):
        return self._protocol

    @property
    def storage(self):
        return self._storage

    @property
    def contact(self):
        return self._our_contact

    @property
    def router(self):
        return self._router

    @router.setter
    def router(self, value):
        self._router = value

    @property
    def our_id(self):
        return self._our_id



