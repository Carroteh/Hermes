import asyncio
import json

from dataclasses import asdict

from hermes.core.Node import Node
from hermes.core.Contact import Contact
from hermes.net.Payload import CommonRequest, PingResponse, FindNodeResponse, ContactResponse, StoreResponse, \
    FindValueResponse, ErrorResponse
from hermes.net.UDPProtocol import UDPProtocol

from hermes.net.RequestHandler import *

class UDPServer:
    def __init__(self, node: Node, host: str, port: int):
        self.node: Node = node
        self.host: str = host
        self.port: int = port
        self.transport = None
        self.handlers = {
            "find_node": self.handle_find_node,
            "find_value": self.handle_find_value,
            "ping": self.handle_ping,
            "store": self.handle_store
        }

    async def start(self):
        loop = asyncio.get_running_loop()
        self.transport, protocol = await loop.create_datagram_endpoint(
            lambda: UDPServerProtocol(self.node, self.handlers),
            local_addr=(self.host, self.port)
        )

        await asyncio.Event().wait()

    async def stop(self):
        if self.transport:
            self.transport.close()

    def handle_ping(self, request: CommonRequest) -> PingResponse:
        self.node.ping(request.sender)
        return PingResponse(random_id=request.random_id)

    def handle_store(self, request:CommonRequest) -> StoreResponse:
        protocol = UDPProtocol("", 0)
        self.node.store(
            Contact(protocol, request.sender),
            request.key,
            request.value,
            request.exp_time
        )
        return StoreResponse(random_id=request.random_id)

    def handle_find_node(self, request: CommonRequest) -> FindNodeResponse:
        protocol = UDPProtocol("", 0)
        contacts, _ = self.node.find_node(Contact(protocol, request.sender), request.key)

        return FindNodeResponse(
            random_id=request.random_id,
            contacts=[ContactResponse(
                contact=c.id,
                protocol_name=c.protocol_name,
                host=c.host,
                port=c.port
            ) for c in contacts]
        )

    def handle_find_value(self, request: CommonRequest) -> FindValueResponse:
        protocol = UDPProtocol("", 0)
        contacts, value = self.node.find_value(Contact(protocol, request.sender), request.key)
        return FindValueResponse(
            random_id=request.random_id,
            contacts=[ContactResponse(
                contact=c.id,
                protocol_name=c.protocol_name,
                host=c.host,
                port=c.port
            ) for c in contacts] if contacts else None,
            value=value
        )

class UDPServerProtocol(asyncio.DatagramProtocol):
    def __init__(self, node: Node, handlers: dict):
        self.node = node
        self.handlers = handlers
        self.transport = None

    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
        async def handle():
            try:
                request_data = json.loads(data.decode())
                request = CommonRequest.from_json(json.dumps(request_data["data"]))
                handler = self.handlers.get(request_data["type"])
                if not handler:
                    response = ErrorResponse(random_id=request.random_id, error_message="Unknown request type.")
                    self.transport.sendto(json.dumps({"type":"error", "data": asdict(response)}).encode(), addr)
                    return
                response = await handler(request)
                self.transport.sendto(json.dumps({"type":request_data["type"]+"Response", "data": asdict(response)}).encode(), addr)
            except Exception as e:
                response = ErrorResponse(random_id=request.random_id, error_message=str(e))
                self.transport.sendto(json.dumps({"type": "error", "data": asdict(response)}).encode(), addr)
        asyncio.create_task(handle())