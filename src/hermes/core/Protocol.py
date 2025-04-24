from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hermes.core.Contact import Contact

from hermes.core.Node import Node
from hermes.core.RPCError import RPCError
from hermes.core.Support import BUCKET_REFRESH_INTERVAL

class Protocol:
    def __init__(self, responds: bool = True, node: Node = None):
        self._responds = responds
        self._node = node

    async def store(self, sender: 'Contact', key: int, val: str, exp_time: int = BUCKET_REFRESH_INTERVAL) -> RPCError:
        """
        Stores the value on the remote peer.
        """
        self._node.store(sender, key, val, exp_time)
        return self.no_error()

    async def find_value(self, sender: 'Contact', key: int) -> (list['Contact'], str, RPCError):
        """
        Returns either contacts close to the key or the value if found.
        """
        contacts, val = await self._node.find_value(sender, key)
        return contacts, val, self.no_error()

    async def find_node(self, sender: 'Contact', key: int) -> (list['Contact'], RPCError):
        contacts, val = await self._node.find_node(sender, key)
        return contacts, self.no_error()

    async def ping(self, sender: 'Contact') -> RPCError:
        if self._responds:
            self._node.ping(sender)
        err = RPCError()
        err.timeout_error = False if self._responds else True
        return RPCError()

    def no_error(self):
        return RPCError()

    @property
    def node(self):
        return self._node

    @node.setter
    def node(self, value):
        self._node = value

    @property
    def responds(self):
        return self._responds

    @responds.setter
    def responds(self, value):
        self._responds = value

