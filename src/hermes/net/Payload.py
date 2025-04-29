import random
import json

from hermes.kademlia.Protocol import Protocol
from typing import Optional
from dataclasses import dataclass, asdict

@dataclass
class BaseRequest:
    protocol_name: str
    random_id: int
    sender: int
    sender_host: str
    sender_port: int

    def to_json(self) -> str:
        return json.dumps(asdict(self))

    @classmethod
    def from_json(cls, json_str: str):
        return cls(**json.loads(json_str))

@dataclass
class FindNodeRequest(BaseRequest):
    key: int

@dataclass
class FindValueRequest(BaseRequest):
    key: int

@dataclass
class PingRequest(BaseRequest):
    pass

@dataclass
class StoreRequest(BaseRequest):
    key: int
    value: str
    exp_time: int

@dataclass
class CommonRequest(BaseRequest):
    protocol_name: str
    random_id: int
    sender: int
    key: Optional[int] = None
    value: Optional[str] = None
    exp_time: int = 0

    @classmethod
    def from_json(cls, json_str: str):
        return cls(**json.loads(json_str))

@dataclass
class BaseResponse:
    random_id: int

    def to_json(self) -> str:
        return json.dumps(asdict(self))

@dataclass
class ErrorResponse(BaseResponse):
    error_message: str

@dataclass
class ContactResponse(BaseResponse):
    contact: int
    protocol_name: str
    host: str
    port: int

@dataclass
class FindNodeResponse(BaseResponse):
    contacts: list[ContactResponse]

@dataclass
class FindValueResponse(BaseResponse):
    contacts: Optional[list[ContactResponse]]
    value: Optional[str]

@dataclass
class PingResponse(BaseResponse):
    pass

@dataclass
class StoreResponse(BaseResponse):
    pass








