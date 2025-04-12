import logging
import asyncio

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hermes.core.Contact import Contact

from hermes.core.Support import B_VAL
from hermes.core.Support import K_VAL
from hermes.core.KBucket import KBucket

logger = logging.getLogger(__name__)

class BucketList:
    def __init__(self, id):
        self._buckets: list[KBucket] = []
        self._buckets.append(KBucket())
        self.id = id
        self.lock = asyncio.Lock()

    async def add_contact(self, contact: 'Contact') -> None:
        """
        Add a contact to the correct bucket.
        If the correct bucket is full, try to split it and try adding again.
        If they bucket already has the contact just refresh it.
        """
        contact.touch()

        # Ensure the following is executed atomically
        while True:
            async with self.lock:

                #Get the appropriate k bucket where the contact should be inserted
                kbucket = self.get_kbucket(contact.id)

                # if its already there, refresh it
                if kbucket.contains(contact.id):
                    logger.info(">>> Contact already in bucket, refreshing.")
                    kbucket.replace_contact(contact)
                    return

                # if the bucket is full try to split it and try again
                if kbucket.is_full():
                    if self.can_split(kbucket):
                        k1, k2 = kbucket.split()
                        index = self.get_kbucket_index(contact.id)

                        # add new buckets to our bucket list
                        self._buckets[index] = k1
                        self._buckets.insert(index+1, k2)
                        self._buckets[index].touch()
                        self._buckets[index+1].touch()

                        # Try adding the contact again, after splitting
                        continue
                    else:
                        pass
                        # TODO ping oldest contact to see if its still around and replace if not
                        return
                else:
                    kbucket.add_contact(contact)
                    return

    def can_split(self, kbucket: KBucket):
            return kbucket.has_in_range(self.id) or (kbucket.depth() % B_VAL) != 0

    def get_kbucket(self, key) -> KBucket:
            return self._buckets[self.get_kbucket_index(key)]

    def get_kbucket_index(self, key) -> int | None:
        """
        Find the appropriate k bucket for the given id.
        """
        for i, bucket in enumerate(self._buckets):
            if bucket.has_in_range(key):
                return i

    async def get_close_contacts(self, key, our_id) -> list['Contact']:
        """"
        Get at most k contacts in the bucket that are closest the given id.
        """
        async with self.lock:
            contacts = [c for b in self._buckets for c in b.contacts if c.id != our_id]
            return sorted(contacts, key=lambda c: c.id ^ key)[:K_VAL]


    @property
    def buckets(self):
        return self._buckets

    @buckets.setter
    def buckets(self, value):
        self._buckets = value

    def __eq__(self, other):
        if not isinstance(other, BucketList):
            return False
        return self.id == other.id


