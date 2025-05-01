from typing import TYPE_CHECKING

from black.lines import Callable

if TYPE_CHECKING:
    from hermes.kademlia.Node import Node


import json
import socket
import logging
import asyncio
from dataclasses import asdict

from hermes.net.Payload import CommonRequest, PingResponse, FindNodeResponse, ContactResponse, StoreResponse, \
    FindValueResponse, ErrorResponse
from hermes.net.UDPProtocol import UDPProtocol
from hermes.kademlia.Contact import Contact

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

    def check_bound_ip(self, host: str):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0)
        try:
            # doesn't even have to be reachable
            s.connect((host, 1))
            ip = s.getsockname()[0]
        except Exception:
            ip = '0.0.0.0'
        finally:
            s.close()
        return ip

    async def start(self, update_addr: Callable):
        loop = asyncio.get_running_loop()
        host = self.check_bound_ip(self.host)
        self.transport, protocol = await loop.create_datagram_endpoint(
            lambda: UDPServerProtocol(self.node, self.handlers),
            local_addr=(host, self.port)
        )
        addr =  self.transport.get_extra_info("sockname")
        update_addr((addr[0], addr[1]))
        logger.info(f"UDP Server started on {addr[0]}:{addr[1]}")

    async def stop(self):
        if self.transport:
            self.transport.close()
        logger.info(f"UDP Server stopped on {self.host}:{self.port}")

    async def handle_ping(self, request: CommonRequest) -> PingResponse:
        contact = Contact(UDPProtocol(request.sender_host, request.sender_port), request.sender, request.sender_host, request.sender_port)
        self.node.ping(contact)
        return PingResponse(random_id=request.random_id)

    async def handle_store(self, request:CommonRequest) -> StoreResponse:
        protocol = UDPProtocol(request.sender_host, request.sender_port)
        await self.node.store(
            Contact(protocol, request.sender, request.sender_host, request.sender_port),
            request.key,
            request.value,
            request.exp_time
        )
        return StoreResponse(random_id=request.random_id)

    async def handle_find_node(self, request: CommonRequest) -> FindNodeResponse:
        protocol = UDPProtocol(request.sender_host, request.sender_port)
        contacts, _ = await self.node.find_node(
            Contact(protocol, request.sender, request.sender_host, request.sender_port),
            request.key
        )

        return FindNodeResponse(
            random_id=request.random_id,
            contacts=[ContactResponse(
                random_id=request.random_id,
                contact=c.id,
                protocol_name='UDPProtocol',
                host=c.host,
                port=c.port
            ) for c in contacts]
        )

    async def handle_find_value(self, request: CommonRequest) -> FindValueResponse:
        protocol = UDPProtocol(request.sender_host, request.sender_port)
        contacts, value = await self.node.find_value(
            Contact(protocol, request.sender, request.sender_host, request.sender_port),
            request.key
        )
        return FindValueResponse(
            random_id=request.random_id,
            contacts=[ContactResponse(
                random_id=request.random_id,
                contact=c.id,
                protocol_name='UDPProtocol',
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
            request = None
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
                if request is not None:
                    response = ErrorResponse(random_id=request.random_id, error_message=str(e))
                else:
                    response = ErrorResponse(random_id=0, error_message="Invalid Protocol.")
                logger.error(f"Sending error to {addr[0]}:{addr[1]}: {str(e)}")
                self.transport.sendto(json.dumps({"type": "error", "data": asdict(response)}).encode(), addr)
        asyncio.create_task(handle())