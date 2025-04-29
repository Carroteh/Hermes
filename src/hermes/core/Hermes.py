import json

from hermes.core.KeyValueTools import KeyValueTools
from hermes.core.KeyValues import *
from hermes.core.Error import Error
from hermes.kademlia.DHT import DHT

class Hermes:
    def __init__(self, nickname: str, dht: DHT):
        self._nickname = nickname
        self._dht = dht
        self._msg_tools = KeyValueTools()

    async def find_by_nickname(self, nickname: str) -> str:
        '''
        Check if the username exists in the DHT
        '''
        key = contact_key(nickname)
        val = None

        found, a, val = await self._dht.find_value(key)

        return val

    async def send_message(self, recipient: str, message: str):
        '''
        Store a message onto the DHT, along with updating its message box
        '''
        # Check recipients existence
        recip = await self.find_by_nickname(recipient)

        if recip is None:
            return Error(user_doesnt_exist=True)

        # Get the shared message box
        msg_box_key = message_box_key(self._nickname, recipient)
        found, a , msg_box_raw = await self._dht.find_value(msg_box_key)

        # If no message box, create one
        if not found:
            msg_box = MessageBoxValue(messages=[])
        else:
            msg_box = MessageValue.from_json(msg_box_raw)

        # Get users public Key
        val = ContactValue.from_json(recip)
        remote_pk = val.public_key

        # Create the message
        msg_key, msg_val = self._msg_tools.create_message(message, self._nickname, recipient, remote_pk)
        # Store msg
        await self._dht.store(msg_key, json.dumps(asdict(msg_val)))

        # Update the msgbox
        msg_box = self._msg_tools.update_message_box(msg_val, msg_box)
        # Store msgbox
        await self._dht.store(msg_box_key, json.dumps(asdict(msg_box)))

        # Check valid recipient
        return Error()

    async def get_messages_from_msg_box(self, sender: str) -> list[LightWeightMessage]:
        '''
        Return a list of messages from a message box
        '''
        returned_msgs: list[LightWeightMessage] = []

        msg_box_key = message_box_key(self._nickname, sender)

        found, a , msg_box_raw = await self._dht.find_value(msg_box_key)

        if not found:
            return []

        msg_box = MessageBoxValue.from_json(msg_box_raw)

        for msg_key in msg_box.message_keys:
            found, a, msg_val_raw = await self._dht.find_value(msg_key)

            if found:
                msg_val = MessageValue.from_json(msg_val_raw)
                decrypted_msg = self._msg_tools.read_message(msg_val.encrypted_message, self._nickname)
                returned_msgs.append(LightWeightMessage(msg_val.timestamp, msg_val.sender, msg_val.receiver, decrypted_msg))

        return returned_msgs
                







    def get_nickname(self):
        return self._nickname

    async def register_nickname(self, nickname: str):
        '''
        Check if a nickname is available, if so register it on the DHT
        '''
        # Check nickname already exists
        contact_value = await self.find_by_nickname(nickname)

        if contact_value is not None:
            return Error(nickname_already_in_use=True)

        contact = ContactValue(nickname, self._dht.contact.host, self._dht.contact.port, self._msg_tools.public_key())

        key = contact_key(nickname)

        await self._dht.store(key, json.dumps(asdict(contact)))

        return Error()

