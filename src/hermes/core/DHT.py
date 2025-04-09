from hermes.core import Protocol
from hermes.core.Contact import Contact
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
        #self._router.dht = self


    def store(self, key: int, val: str):
        """
        Store a key value pair on the DHT. (on K closer contacts
        """
        self._touch_bucket_with_key(key)
        self._storage.set(key, val)
        self._store_on_closer_contacts(key, val)

    def find_value(self, key: int) -> (bool, list[Contact], str):
        self._touch_bucket_with_key(key)

        our_val = None
        contacts_queried: list[Contact] = []

        # Return is Found, contacts, val
        ret = (False, None, None)

        if self._storage.contains(key):
            ret = (True, None, self._storage.get(key))
        else:
            found, contacts, found_by, val = self._router.lookup(key, self.router.rpc_find_nodes)

            if found:
                ret = (True, None, val)

                #



    @property
    def router(self):
        return self._router

    @router.setter
    def router(self, value):
        self._router = value

    def _touch_bucket_with_key(self, key):
        pass

