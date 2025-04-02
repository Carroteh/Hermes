from hermes.core.Contact import Contact
from hermes.core.KBucket import KBucket
import asyncio

class BucketList:
    def __init__(self, id):
        self._buckets = []
        self.id = id
        self.lock = asyncio.Lock()

    async def add_contact(self, contact):
        """
        Add a contact to the correct bucket.
        If the correct bucket is full, try to split it and try adding again.
        IF they bucket already has the contact just refresh it.
        """
        contact.touch()

        recurse = False
        # Ensure the following is executed atomically
        while True:
            async with self.lock:

                #Get the appropriate k bucket where the contact should be inserted
                kbucket = self.get_kbucket(contact.id)

                # if its already there, refresh it
                if kbucket.contains(contact.id):
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
                        continue
                    else:
                        pass
                        # TODO ping oldest contact to see if its still around and replace if not
                        return
                else:
                    kbucket.add_contact(contact)
                    return





    def can_split(self, kbucket: KBucket):
        pass

    def get_kbucket(self, id) -> KBucket:
        pass

    def get_kbucket_index(self, id) -> int:
        pass

    @property
    def buckets(self):
        return self._buckets

    @buckets.setter
    def buckets(self, value):
        self._buckets = value


