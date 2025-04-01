
class BucketList:
    def __init__(self, id):
        self._buckets = []
        self.id = id

    def add_contact(self, contact):
        pass

    @property
    def buckets(self):
        return self._buckets

    @buckets.setter
    def buckets(self, value):
        self._buckets = value


