from typing import TYPE_CHECKING

from hermes.net.UDPServer import UDPServer

if TYPE_CHECKING:
    from hermes.core.Contact import Contact

from hermes.core.BucketList import BucketList
from hermes.core.Storage import Storage

class Node:
    def __init__(self, our_contact: Contact, storage: Storage):
        self._our_contact = our_contact
        self._storage: Storage = storage
        self._bucket_list: BucketList = BucketList(our_contact.id)
        self._server = UDPServer(self, our_contact.host, our_contact.port)

    def ping(self, sender):
        return self._our_contact

    def store(self, sender: 'Contact', key: int, val: str, expiration: int = 0):
        """
        Store a key value pair
        """
        assert sender.id != self._our_contact.id, "Sender cannot be us!"

        self._bucket_list.add_contact(sender)
        self._storage.set(key, val, expiration)
        self.send_key_values_if_new(sender)

    async def find_node(self, sender, key) -> (list['Contact'], int):
        """
        Finds a node by their key

        Returns
            list of nodes close to the key
        """
        assert sender.id != self._our_contact.id, "Sender cannot be us!"
        self.send_key_values_if_new(sender)
        await self._bucket_list.add_contact(sender)

        contacts = await self._bucket_list.get_close_contacts(key, sender.id)

        return contacts, None

    async def find_value(self, sender, key) -> (list['Contact'], str):
        """
        Find the value associated with the given key. If not found, return a list of close contacts.
        """

        assert sender.id != self._our_contact.id, "Sender cannot be us!"

        await self._bucket_list.add_contact(sender)
        self.send_key_values_if_new(sender)

        if self._storage.contains(key):
            return None, self._storage.get(key)
        else:
            return await self._bucket_list.get_close_contacts(key, sender.id), None

    def send_key_values_if_new(self, sender):
        pass

    @property
    def our_contact(self):
        return self._our_contact

    @property
    def storage(self):
        return self._storage

    @storage.setter
    def storage(self, value):
        self._storage = value

    @property
    def bucket_list(self):
        return self._bucket_list

    @property
    def server(self):
        return self._server

