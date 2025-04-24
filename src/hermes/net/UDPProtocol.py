import asyncio
import json
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hermes.core.Contact import Contact

import random

from hermes.core.Node import Node
from hermes.core.Protocol import Protocol
from hermes.core.RPCError import RPCError
from hermes.net.Payload import *
from hermes.core.Support import REQUEST_TIMEOUT, BUCKET_REFRESH_INTERVAL


class UDPProtocol(Protocol):
    '''
    Class that implements the networking side of the kademlia protocol using UDP
    '''

    def __init__(self, host: str, port: int, node: Node = None):
        super().__init__(node=node)
        self._host = host
        self._port = port

    async def find_node(self, sender: 'Contact', key: int) -> (list['Contact'], RPCError):
        random_id = random.randint(0, 2**160-1)

        request = FindNodeRequest(
            protocol_name=self.__class__.__name__,
            random_id=random_id,
            sender=sender.id,
            key=key
        )

        request_data = {"type": "find_node", "data": asdict(request)}
        loop = asyncio.get_running_loop()
        transport, protocol = await loop.create_datagram_endpoint(
            lambda: UDPClientHandler(),
            local_addr=("0.0.0.0", 0)
        )

        try:
            # Send datagram
            transport.sendto(json.dumps(request_data).encode(), (self._host, self._port))
            data, _ = await asyncio.wait_for(protocol.receive(), REQUEST_TIMEOUT)
            response = json.loads(data)

            # Check for error from remote node
            if response["type"] == "Error":
                error = ErrorResponse(**response["data"])
                return [], RPCError(peer_error=True, peer_error_message=error.error_message)
            # Check if echoed id matches
            if response["data"]["random_id"] != random_id:
                return [], RPCError(id_mismatched_error=True)

            # Get the response, and repackage
            response = FindNodeResponse(**response["data"])
            contacts = [
                Contact(
                    UDPProtocol(host=c.host, port=c.port),
                    c.contact,
                    host=c.host,
                    port=c.port
                )
                for c in response.contacts
                if c.protocol_name == self.__class__.__name__
            ]
            return contacts, RPCError()

        except asyncio.TimeoutError:
            return [], RPCError(timeout_error=True)
        except Exception as e:
            return [], RPCError(protocol_error=True, peer_error_message=str(e))
        finally:
            transport.close()

    async def find_value(self, sender: 'Contact', key: int) -> (list['Contact'], RPCError):
        random_id = random.randint(0, 2 ** 160 - 1)

        request = FindValueRequest(
            protocol_name=self.__class__.__name__,
            random_id=random_id,
            sender=sender.id,
            key=key
        )

        request_data = {"type": "find_value", "data": asdict(request)}
        loop = asyncio.get_running_loop()
        transport, protocol = await loop.create_datagram_endpoint(
            lambda: UDPClientHandler(),
            local_addr=("0.0.0.0", 0)
        )

        try:
            transport.sendto(json.dumps(request_data).encode(), (self._host, self._port))
            data, _ = await asyncio.wait_for(protocol.receive(), REQUEST_TIMEOUT)
            response = json.loads(data.decode())
            if response["type"] == "Error":
                error = ErrorResponse(**response["data"])
                return [], RPCError(peer_error=True, peer_error_message=error.error_message)
            if response["data"]["random_id"] != random_id:
                return [], RPCError(id_mismatched_error=True)
            response = FindValueResponse(**response["data"])
            contacts = [
                Contact(
                    UDPProtocol(c.host, c.port),
                    c.contact,
                    host=c.host,
                    port=c.port
                ) for c in response.contacts
                if c.protocol_name == self.__class__.__name__
            ]
            return contacts, RPCError()
        except asyncio.TimeoutError:
            return [], RPCError(timeout_error=True)
        except Exception as e:
            return [], RPCError(protocol_error=True, peer_error_message=str(e))
        finally:
            transport.close()

    async def ping(self, sender: 'Contact') -> RPCError:
        random_id = random.randint(0, 2 ** 160 - 1)

        request = PingRequest(
            protocol_name=self.__class__.__name__,
            random_id=random_id,
            sender=sender.id,
        )

        request_data = {"type": "ping", "data": asdict(request)}
        loop = asyncio.get_running_loop()
        transport, protocol = await loop.create_datagram_endpoint(
            lambda: UDPClientHandler(),
            local_addr=("0.0.0.0", 0)
        )

        try:
            transport.sendto(json.dumps(request_data).encode(), (self._host, self._port))
            data, _ = await asyncio.wait_for(protocol.receive(), REQUEST_TIMEOUT)
            response = json.loads(data.decode())

            if response["type"] == "Error":
                error = ErrorResponse(**response["data"])
                return RPCError(peer_error=True, peer_error_message=error.error_message)
            if response["data"]["random_id"] != random_id:
                return RPCError(id_mismatched_error=True)
            return RPCError()
        except asyncio.TimeoutError:
            return RPCError(timeout_error=True)
        except Exception as e:
            return RPCError(protocol_error=True, peer_error_message=str(e))
        finally:
            transport.close()

    async def store(self, sender: 'Contact', key: int, val: str, exp_time: int = BUCKET_REFRESH_INTERVAL) -> RPCError:
        random_id = random.randint(0, 2 ** 160 - 1)

        request = StoreRequest(
            protocol_name=self.__class__.__name__,
            random_id=random_id,
            sender=sender.id,
            key=key,
            value=val,
            exp_time=exp_time
        )

        request_data = {"type": "store", "data": asdict(request)}
        loop = asyncio.get_running_loop()
        transport, protocol = await loop.create_datagram_endpoint(
            lambda: UDPClientHandler(),
            local_addr=("0.0.0.0", 0)
        )

        try:
            transport.sendto(json.dumps(request_data).encode(), (self._host, self._port))
            data, _ = await asyncio.wait_for(protocol.receive(), REQUEST_TIMEOUT)
            response = json.loads(data.decode())

            if response["type"] == "Error":
                error = ErrorResponse(**response["data"])
                return RPCError(peer_error=True, peer_error_message=error.error_message)
            if response["data"]["random_id"] != random_id:
                return RPCError(id_mismatched_error=True)
            return RPCError()
        except asyncio.TimeoutError:
            return RPCError(timeout_error=True)
        except Exception as e:
            return RPCError(protocol_error=True, peer_error_message=str(e))
        finally:
            transport.close()

class UDPClientHandler(asyncio.DatagramProtocol):
    def __init__(self):
        self.future = asyncio.Future()

    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
        if not self.future.done():
            self.future.set_result(data)

    async def receive(self):
        return await self.future

