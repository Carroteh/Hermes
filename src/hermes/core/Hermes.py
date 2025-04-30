import json

from hermes.core.KeyValueTools import KeyValueTools
from hermes.core.KeyValues import *
from hermes.core.Error import Error
from hermes.kademlia.DHT import DHT

class Hermes:
    def __init__(self, dht: DHT):
        self._nickname: str = None
        self._dht: DHT = dht
        self._msg_tools = KeyValueTools()

    def connected(self) -> bool:
        return self._dht.router.node.bucket_list.get_num_contacts() > 0

    async def find_by_nickname(self, nickname: str) -> str:
        '''
        Check if the username exists in the DHT
        '''

        key = contact_key(nickname)
        val = None

        found, a, val = await self._dht.find_value(key)

        return val

    async def send_message(self, recipient: str, message: str) -> Error:
        '''
        Store a message onto the DHT, along with updating its message box
        '''
        if not self.connected():
            return Error(isolated=True, error_message="Node is isolated. Try bootstrapping.")

        if self._nickname == recipient:
            return Error(query_with_self=True, error_message="Cannot query with self.")

        if self._nickname is None:
            return Error(not_registered=True, error_message="Not registered.")

        # Check recipients existence
        recip = await self.find_by_nickname(recipient)

        if recip is None:
            return Error(user_doesnt_exist=True, error_message="Recipient doesn't exist.")

        # Get the shared message box
        msg_box_key = message_box_key(self._nickname, recipient)
        found, a , msg_box_raw = await self._dht.find_value(msg_box_key)

        # If no message box, create one
        if not found:
            msg_box = MessageBoxValue(message_keys=[])
        else:
            msg_box = MessageBoxValue.from_json(msg_box_raw)

        # Get users public Key
        val = ContactValue.from_json(recip)
        remote_pk = val.public_key

        # Create the message
        msg_key, msg_val = self._msg_tools.create_message(message, self._nickname, recipient, remote_pk)
        # Store msg
        await self._dht.store(msg_key, json.dumps(asdict(msg_val)))

        # Update the msgbox
        msg_box = self._msg_tools.update_message_box(msg_val, msg_box, msg_key)
        # Store msgbox
        await self._dht.store(msg_box_key, json.dumps(asdict(msg_box)))

        # Check valid recipient
        return Error()

    async def get_messages_from_msg_box(self, sender: str) -> (list[LightWeightMessage], Error):
        '''
        Return a list of messages from a message box
        '''
        if not self.connected():
            return Error(isolated=True, error_message="Node is isolated. Try bootstrapping.")

        if self._nickname is None:
            return [], Error(not_registered=True, error_message="Not registered.")

        if self._nickname == sender:
            return [], Error(query_with_self=True, error_message="Cannot query with self.")

        nick = await self.find_by_nickname(sender)

        if nick is None:
            return Error(user_doesnt_exist=True, error_message="Sender doesn't exist.")

        returned_msgs: list[LightWeightMessage] = []

        msg_box_key = message_box_key(self._nickname, sender)

        found, a , msg_box_raw = await self._dht.find_value(msg_box_key)

        if not found:
            return [], Error()

        msg_box = MessageBoxValue.from_json(msg_box_raw)

        for msg_key in msg_box.message_keys:
            found, a, msg_val_raw = await self._dht.find_value(msg_key)

            if found:
                msg_val = MessageValue.from_json(msg_val_raw)
                decrypted_msg = self._msg_tools.read_message(msg_val, self._nickname)
                returned_msgs.append(LightWeightMessage(msg_val.timestamp, msg_val.sender, msg_val.receiver, decrypted_msg))

        return returned_msgs, Error()

    def get_nickname(self):
        return self._nickname

    async def register_nickname(self, nickname: str) -> Error:
        '''
        Check if a nickname is available, if so register it on the DHT
        '''
        if not self.connected():
            return Error(isolated=True, error_message="Node is isolated. Try bootstrapping.")

        # Check already registered
        if self._nickname is not None:
            return Error(already_registered=True, error_message="This node already has a registered nickname.")

        # Check nickname already exists
        contact_value = await self.find_by_nickname(nickname)

        if contact_value is not None:
            return Error(nickname_already_in_use=True, error_message="Nickname already in use.")

        contact = ContactValue(nickname, self._dht.contact.host, self._dht.contact.port, self._msg_tools.public_key())

        key = contact_key(nickname)

        await self._dht.store(key, json.dumps(asdict(contact)))

        self._nickname = nickname

        return Error()

