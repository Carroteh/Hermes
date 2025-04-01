from hermes.core.Contact import Contact


class Node:
    def __init__(self, our_contact, storage):
        self._our_contact = our_contact
        self._storage = storage
        self._bucket_list = []

    def ping(self, sender):
        return self._our_contact

    def store(self, key, value):
        pass

    def find_node(self, sender, key):
        pass

    def find_value(self, sender, key):
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
