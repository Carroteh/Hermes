import hashlib
import datetime
import json

from dataclasses import dataclass, asdict

@dataclass
class BaseValue:
    def to_json(self) -> str:
        return json.dumps(asdict(self))

    @classmethod
    def from_json(cls, json_str: str):
        return cls(**json.loads(json_str))

@dataclass
class MessageValue(BaseValue):
    sender: str
    receiver: str
    encrypted_message : str
    timestamp : str
    # [sender, receiver]
    wrapped_keys: list[str]
    type: str = "message"

@dataclass
class MessageBoxValue(BaseValue):
    message_keys: list[int]

@dataclass
class ContactValue(BaseValue):
    name: str
    ip_address: str
    udp_port: int
    public_key: str
    tcp_port: int

@dataclass
class LightWeightMessage:
    timestamp: float
    sender: str
    receiver: str
    message: str

def contact_key(name: str) -> int:
    return int(hashlib.sha1(f"contact_{name}".encode()).hexdigest(), 16)

def message_box_key(user1: str, user2: str):
    '''
    The user names are sorted to ensure that the key is consistent.
    '''
    ordered = sorted([user1, user2])
    return int(hashlib.sha1(f"message_box_{ordered[0]}{ordered[1]}".encode()).hexdigest(), 16)

def message_key(sender: str, receiver: str) -> int:
    timestamp = datetime.datetime.now().timestamp()
    return int(hashlib.sha1(f"msg_{sender}{receiver}{timestamp}".encode()).hexdigest(), 16)

