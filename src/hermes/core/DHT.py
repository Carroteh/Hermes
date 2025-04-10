from hermes.core.Protocol import Protocol
from hermes.core.Contact import Contact
from hermes.core.RPCError import RPCError
from hermes.core.Storage import Storage
from hermes.core.Router import Router
from hermes.core.Node import Node


class DHT:
    def __init__(self, id: int, protocol: Protocol, storage: Storage, router: Router):
        self._router: Router = router
        self._storage: Storage = storage
        self._protocol:Protocol = protocol
        self._our_id: int = id
        self._our_contact: Contact = Contact(protocol, id)
        self._node: Node = Node(self._our_contact, storage)
        self._router.node = self._node
        self._router.set_error_handler(self.handle_error)


    def store(self, key: int, val: str):
        """
        Store a key value pair on the DHT. (on K closer contacts
        """
        self._touch_bucket_with_key(key)
        self._storage.set(key, val)
        self._store_on_closer_contacts(key, val)

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
                    error = store_to.protocol.store(self._node.our_contact, key, val, 100000)
                    self.handle_error(error, store_to)
        return ret

    def _touch_bucket_with_key(self, key):
        pass

    def _store_on_closer_contacts(self, key, val):
        pass

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

