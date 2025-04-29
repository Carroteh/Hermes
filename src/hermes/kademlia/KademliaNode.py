
from crypt.Crypt import Crypt
from core.KBucket import KBucket
from core.Support import Triple
import hashlib


class KademliaNode:
    def __init__(self, name : str):
        self._crypt = Crypt()
        pre_hash = bytes(self._crypt.get_public_key()) + name.encode()
        self._id = int(hashlib.sha1(pre_hash).hexdigest(),16)
        self._buckets : list[KBucket]  = [KBucket() for i in range(0,160)]

        self._buckets[0].add(triple=Triple("localhost", 12, self._id))
        print(self._buckets[0])
        self._buckets[0].add(triple=Triple("localhoste", 12, self._id))
        print(self._buckets[0])
        self._buckets[0].add(triple=Triple("localhostee", 12, self._id))
        print(self._buckets[0])

        self._buckets[0].evict(Triple("localhost", 12, self._id))
        print(self._buckets[0])

        self._buckets[0].refresh_entry(Triple("localhoste", 12, self._id))
        print(self._buckets[0])
        
    def __repr__(self):
        s = f"{self._id}:"
        s += [ "\n".join(repr(bucket) for bucket in self._buckets)]
        return s

    def xor_distance(self, x, y):
        return x ^ y