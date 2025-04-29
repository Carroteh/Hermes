import asyncio
import json
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hermes.kademlia.Node import Node

import random
import logging

from hermes.kademlia.Protocol import Protocol
from hermes.kademlia.RPCError import RPCError
from hermes.kademlia.Contact import Contact
from hermes.net.Payload import *
from hermes.kademlia.Support import REQUEST_TIMEOUT, BUCKET_REFRESH_INTERVAL

logger = logging.getLogger(__name__)

class UDPProtocol(Protocol):
    '''
    Class that implements the networking side of the kademlia protocol using UDP
    '''

    def __init__(self, host: str, port: int, node: 'Node' = None):
        super().__init__(node=node)
        self._host = host
        self._port = port

    async def find_node(self, sender: Contact, key: int) -> (list[Contact], RPCError):
        random_id = random.randint(0, 2**160-1)

        request = FindNodeRequest(
            protocol_name=self.__class__.__name__,
            random_id=random_id,
            sender=sender.id,
            sender_host=sender.host,
            sender_port=sender.port,
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
            logger.info(f"Sending FIND_NODE RPC to: {self._host}:{self._port}")
            transport.sendto(json.dumps(request_data).encode(), (self._host, self._port))
            data, _ = await asyncio.wait_for(protocol.receive(), REQUEST_TIMEOUT)
            response = json.loads(data)

            # Check for error from remote node
            if response["type"] == "error":
                error = ErrorResponse(**response["data"])
                logger.error(f"FIND_NODE Error response from: {self._host}:{self._port} sent error: {error.error_message}")
                return [], RPCError(peer_error=True, peer_error_message=error.error_message)
            # Check if echoed id matches
            if response["data"]["random_id"] != random_id:
                logger.error(f"FIND_NODE Error: id_mismatch_error")
                return [], RPCError(id_mismatched_error=True)

            # Get the response, and repackage
            response = FindNodeResponse(**response["data"])

            if response.contacts is not None:
                contacts = [
                    Contact(
                        UDPProtocol(host=c['host'], port=c['port']),
                        c['contact'],
                        host=c['host'],
                        port=c['port']
                    )
                    for c in response.contacts
                ]
                logger.info(f"FIND_NODE returned {len(contacts)} contacts from {self._host}:{self._port}")
                return contacts, RPCError()
            else:
                logger.info(f"FIND_NODE returned NOTHING from {self._host}:{self._port}")
                return [], RPCError()

        except asyncio.TimeoutError:
            logger.error(f"FIND_NODE timed out on {self._host}:{self._port}")
            return [], RPCError(timeout_error=True)
        except Exception as e:
            logger.error(f"FIND_NODE Error: {str(e)}")
            return [], RPCError(protocol_error=True, peer_error_message=str(e))
        finally:
            transport.close()

    async def find_value(self, sender: Contact, key: int) -> (list[Contact], str, RPCError):
        random_id = random.randint(0, 2 ** 160 - 1)

        request = FindValueRequest(
            protocol_name=self.__class__.__name__,
            random_id=random_id,
            sender=sender.id,
            sender_host=sender.host,
            sender_port=sender.port,
            key=key
        )

        request_data = {"type": "find_value", "data": asdict(request)}
        loop = asyncio.get_running_loop()
        transport, protocol = await loop.create_datagram_endpoint(
            lambda: UDPClientHandler(),
            local_addr=("0.0.0.0", 0)
        )

        try:
            logger.info(f"Sending FIND_VALUE RPC to: {self._host}:{self._port}")
            transport.sendto(json.dumps(request_data).encode(), (self._host, self._port))
            data, _ = await asyncio.wait_for(protocol.receive(), REQUEST_TIMEOUT)
            response = json.loads(data.decode())

            if response["type"] == "error":
                error = ErrorResponse(**response["data"])
                logger.error(f"FIND_VALUE Error response from: {self._host}:{self._port} sent error: {error.error_message}")
                return [], None, RPCError(peer_error=True, peer_error_message=error.error_message)
            if response["data"]["random_id"] != random_id:
                logger.error("FIND_VALUE Error: id_mismatch_error")
                return [], None, RPCError(id_mismatched_error=True)
            response = FindValueResponse(**response["data"])

            if response.value is not None:
                logger.info(f"FIND_VALUE returned value from {self._host}:{self._port}")
                return [], response.value, RPCError()
            else:
                if response.contacts is not None:
                    logger.info(f"FIND_VALUE returned {len(response.contacts)} contacts from {self._host}:{self._port}")
                    contacts = [
                        Contact(
                            UDPProtocol(host=c['host'], port=c['port']),
                            c['contact'],
                            host=c['host'],
                            port=c['port']
                        ) for c in response.contacts
                    ]
                    return contacts, None, RPCError()
                else:
                    logger.info(f"FIND_VALUE returned NOTHING from {self._host}:{self._port}")
                    return [], None, RPCError()
        except asyncio.TimeoutError:
            logger.error(f"FIND_VALUE timed out on {self._host}:{self._port}")
            return [], None, RPCError(timeout_error=True)
        except Exception as e:
            logger.error(f"FIND_VALUE Error: {str(e)}")
            return [], None, RPCError(protocol_error=True, peer_error_message=str(e))
        finally:
            transport.close()

    async def ping(self, sender: Contact) -> RPCError:
        random_id = random.randint(0, 2 ** 160 - 1)

        request = PingRequest(
            protocol_name=self.__class__.__name__,
            random_id=random_id,
            sender=sender.id,
            sender_host=sender.host,
            sender_port=sender.port,
        )

        request_data = {"type": "ping", "data": asdict(request)}
        loop = asyncio.get_running_loop()
        transport, protocol = await loop.create_datagram_endpoint(
            lambda: UDPClientHandler(),
            local_addr=("0.0.0.0", 0)
        )

        try:
            logger.info(f"Sending PING RPC to: {self._host}:{self._port}")
            transport.sendto(json.dumps(request_data).encode(), (self._host, self._port))
            data, _ = await asyncio.wait_for(protocol.receive(), REQUEST_TIMEOUT)
            response = json.loads(data.decode())

            if response["type"] == "error":
                error = ErrorResponse(**response["data"])
                logger.error(f"PING Error response from: {self._host}:{self._port} sent error: {error.error_message}")
                return RPCError(peer_error=True, peer_error_message=error.error_message)
            if response["data"]["random_id"] != random_id:
                logger.error("PING Error: id_mismatch_error")
                return RPCError(id_mismatched_error=True)
            logger.info(f"PING successful to {self._host}:{self._port}")
            return RPCError()
        except asyncio.TimeoutError:
            logger.error(f"PING timed out on {self._host}:{self._port}")
            return RPCError(timeout_error=True)
        except Exception as e:
            logger.error(f"PING Error: {str(e)}")
            return RPCError(protocol_error=True, peer_error_message=str(e))
        finally:
            transport.close()

    async def store(self, sender: Contact, key: int, val: str, exp_time: int = BUCKET_REFRESH_INTERVAL) -> RPCError:
        random_id = random.randint(0, 2 ** 160 - 1)

        request = StoreRequest(
            protocol_name=self.__class__.__name__,
            random_id=random_id,
            sender=sender.id,
            sender_host=sender.host,
            sender_port=sender.port,
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
            logger.info(f"Sending STORE RPC to: {self._host}:{self._port}")
            transport.sendto(json.dumps(request_data).encode(), (self._host, self._port))
            data, _ = await asyncio.wait_for(protocol.receive(), REQUEST_TIMEOUT)
            response = json.loads(data.decode())

            if response["type"] == "error":
                error = ErrorResponse(**response["data"])
                logger.error(f"STORE Error response from: {self._host}:{self._port} sent error: {error.error_message}")
                return RPCError(peer_error=True, peer_error_message=error.error_message)
            if response["data"]["random_id"] != random_id:
                logger.error("STORE Error: id_mismatch_error")
                return RPCError(id_mismatched_error=True)

            logger.info(f"STORE successful to {self._host}:{self._port}")
            return RPCError()

        except asyncio.TimeoutError:
            logger.error(f"STORE timed out on {self._host}:{self._port}")
            return RPCError(timeout_error=True)
        except Exception as e:
            logger.error(f"STORE Error: {str(e)}")
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
            self.future.set_result((data, addr))

    async def receive(self):
        return await self.future

