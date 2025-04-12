from core.Support import Triple
from core.Support import K_VAL

class KBucket_old:
    def __init__(self):
        self._bucket : list[Triple] = []

    def add(self, triple : Triple) -> bool:
        if len(self._bucket) == K_VAL:
            return False
        self._bucket.append(triple)
        return True
    
    def get_old(self) -> Triple:
        return self._bucket[0]
    
    def refresh_entry(self, triple : Triple) -> None:
        self._bucket.remove(triple)
        self._bucket.append(triple)

    def evict(self, triple : Triple) -> None:
        self._bucket.remove(triple)
        
    def __repr__(self):
        s = "\n------K-BUCKET-------"
        s += "\n".join([repr(triple) for triple in self._bucket])
        return s