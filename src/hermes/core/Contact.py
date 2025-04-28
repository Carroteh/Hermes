import json

from hermes.core.Protocol import Protocol
import datetime
from dataclasses import dataclass, asdict

@dataclass
class Contact:
    protocol: Protocol
    id: int
    host: str = ""
    port: int = 0
    last_seen = datetime.datetime.now()

    def to_json(self) -> str:
        return json.dumps(asdict(self))

    @classmethod
    def from_json(cls, json_str: str):
        return cls(**json.loads(json_str))

    def touch(self):
        self.last_seen = datetime.datetime.now()

    def __repr__(self):
        return f"ID: {self.id} ~ HOST: {self.host} ~ PORT: {self.port} Last Seen: {self.last_seen}"

    def __eq__(self, other):
        if not isinstance(other, Contact):
            return NotImplemented
        return self.id == other.id