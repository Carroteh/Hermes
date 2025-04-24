from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hermes.core.Node import Node


import json
import logging
from dataclasses import asdict

from hermes.net.Payload import CommonRequest, PingResponse, FindNodeResponse, ContactResponse, StoreResponse, \
    FindValueResponse, ErrorResponse
from hermes.net.UDPProtocol import UDPProtocol
from hermes.core.Contact import Contact
from hermes.net.RequestHandler import *

logger = logging.getLogger(__name__)

class UDPServer:
    def __init__(self, node: 'Node', host: str, port: int):
        self.node: 'Node' = node
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

    async def handle_ping(self, request: CommonRequest) -> PingResponse:
        self.node.ping(request.sender)
        return PingResponse(random_id=request.random_id)

    async def handle_store(self, request:CommonRequest) -> StoreResponse:
        protocol = UDPProtocol("", 0)
        self.node.store(
            Contact(protocol, request.sender),
            request.key,
            request.value,
            request.exp_time
        )
        return StoreResponse(random_id=request.random_id)

    async def handle_find_node(self, request: CommonRequest) -> FindNodeResponse:
        protocol = UDPProtocol("", 0)
        contacts, _ = await self.node.find_node(Contact(protocol, request.sender), request.key)

        return FindNodeResponse(
            random_id=request.random_id,
            contacts=[ContactResponse(
                contact=c.id,
                protocol_name=c.protocol_name,
                host=c.host,
                port=c.port
            ) for c in contacts]
        )

    async def handle_find_value(self, request: CommonRequest) -> FindValueResponse:
        protocol = UDPProtocol("", 0)
        contacts, value = await self.node.find_value(Contact(protocol, request.sender), request.key)
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
    def __init__(self, node: 'Node', handlers: dict):
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
                logger.info(f"Received {request_data['type'].upper()} request from {addr[0]}:{addr[1]}")

                if not handler:
                    response = ErrorResponse(random_id=request.random_id, error_message="Unknown request type.")
                    self.transport.sendto(json.dumps({"type":"error", "data": asdict(response)}).encode(), addr)
                    return

                response = await handler(request)

                logger.info(f"Sending {request_data['type'].upper()}_RESPONSE to {addr[0]}:{addr[1]}")
                self.transport.sendto(json.dumps({"type":request_data["type"]+"_response", "data": asdict(response)}).encode(), addr)
            except Exception as e:
                response = ErrorResponse(random_id=request.random_id, error_message=str(e))
                logger.error(f"Sending error to {addr[0]}:{addr[1]}: {str(e)}")
                self.transport.sendto(json.dumps({"type": "error", "data": asdict(response)}).encode(), addr)
        asyncio.create_task(handle())