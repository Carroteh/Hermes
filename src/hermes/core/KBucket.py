import datetime

from hermes.core.KBucket_old import KBucket
from hermes.core.Support import K_VAL

class KBucket:
    def __init__(self, low=None, high=None):
        self.timestamp = None
        self._contacts = []
        if low is not None and high is not None:
            self._low = low
            self._high = high
        else:
            self._low = 0
            self._high = 2 ** 160

    def touch(self):
        """
        Updates the timestamp of the object to the current date and time.
        """
        self.timestamp = datetime.datetime.now()

    def add_contact(self, contact):
        """
        Adds a contact to the list of managed contacts if there is sufficient space
        available in the bucket. Throws an exception if the bucket already contains
        the maximum allowable number of contacts.

        Args:
            contact: The contact object to be added to the list of managed contacts.

        Raises:
            Exception: If the bucket is already at its maximum capacity as defined
            by the constant K_VAL.
        """
        if len(self._contacts)  >= K_VAL:
            raise Exception("KBucket is full")
        self._contacts.append(contact)

    def contains(self, id):
        """
        Checks if a contact with a given ID is already present in the bucket.

        Args:
            id: The ID of the contact to be searched for.
        """
        for contact in self._contacts:
            if contact.id == id:
                return True
        return False

    def replace_contact(self, new_contact):
        """
        Replaces the contact with the same id in the bucket with the new contact.
        Used to update network info and LastSeen values.
        """
        for i, contact in enumerate(self._contacts):
            if contact.id == new_contact.id:
                self._contacts[i] = new_contact
                return

    def split(self) -> (KBucket, KBucket):
        #TODO
        pass

    def is_full(self):
        return len(self._contacts) == K_VAL

    @property
    def contacts(self):
        return self._contacts

    @contacts.setter
    def contacts(self, value):
        self._contacts = value

    @property
    def low(self):
        return self._low

    @low.setter
    def low(self, value):
        self._low = value

    @property
    def high(self):
        return self._high

    @high.setter
    def high(self, value):
        self._high = value
