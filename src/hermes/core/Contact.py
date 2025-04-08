from hermes.core.Protocol import Protocol
import datetime

class Contact:
    def __init__(self, protocol, id):
        self.protocol = protocol
        self.id = id
        self.last_seen = datetime.datetime.now()

    def touch(self):
        self.last_seen = datetime.datetime.now()

    def __repr__(self):
        return f"ID: {self.id} ~ Last Seen: {self.last_seen}"

    def __eq__(self, other):
        if not isinstance(other, Contact):
            return NotImplemented
        return self.id == other.id