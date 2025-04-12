from __future__ import annotations

import datetime
import logging

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hermes.core.Contact import Contact

from hermes.core.Support import K_VAL

logger = logging.getLogger(__name__)

class KBucket:
    def __init__(self, low=None, high=None):
        self.timestamp: datetime = datetime.datetime.now()
        self._contacts: list['Contact'] = []
        if low is not None and high is not None:
            self._low = low
            self._high = high
        else:
            self._low = 0
            self._high = 2 ** 160
        self._key = high

    def touch(self):
        """
        Updates the timestamp of the object to the current date and time.
        """
        self.timestamp = datetime.datetime.now()

    def add_contact(self, contact: 'Contact'):
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
        logger.info(">>> Added contact: " + str(contact))

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
        """
        Splits the current KBucket into two smaller KBuckets. Contacts within the
        current KBucket are reallocated to the new KBuckets based on their ID values.

        Returns (KBucket, KBucket): The two new KBuckets created from the current one.
        """
        logger.info(">>> Splitting bucket. Reorganizing contacts.")

        mid = (self._low + self._high) // 2
        k1 = KBucket(self._low, mid)
        k2 = KBucket(mid + 1, self._high)

        # Reorganize the contacts into the new kbuckets
        for contact in list(self._contacts):
            if k1.low <= contact.id <= k1.high:
                k1.add_contact(contact)
            else:
                k2.add_contact(contact)
        return k1, k2

    def has_in_range(self, id):
        return self._low <= id <= self._high

    def depth(self) -> int:
        """
        Find the number of common bits among all contacts
        If no contacts, or shared bits, return 0
        """

        # Create a list of bit strings of all contact ids
        bits: list[str] = [str(bin(contact.id))[2:] for contact in self._contacts]
        shared_bits: str = ''

        if len(self._contacts) > 0:
            # Start at first contact
            shared_bits = bits[0]

            # Loop through all other contacts
            for i in range(1, len(bits)):
                # Loop through shared bits
                for j in range(len(shared_bits)):
                    # When bits start mismatching, stop and update shared_bits to just before that
                    if shared_bits[j] != bits[i][j]:
                        shared_bits = shared_bits[:i]
                        break

        return len(shared_bits)

    def is_full(self):
        """
        Returns True if the bucket is full, False otherwise.
        """
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

    @property
    def key(self):
        return self._key
