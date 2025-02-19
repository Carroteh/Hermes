
from crypt.Crypt import Crypt
import hashlib



class KademliaNode:
    def __init__(self, name : str):
        self._crypt = Crypt()
        pre_hash = bytes(self._crypt.get_public_key()) + name.encode()
        self._id = hashlib.sha1(pre_hash).hexdigest()

    def xor_distance(self, x, y):
        return x ^ y