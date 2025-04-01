import datetime
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
        self.timestamp = datetime.datetime.now()

    def add_contact(self, contact):
        if len(self._contacts)  >= K_VAL:
            raise Exception("KBucket is full")
        self._contacts.append(contact)

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
