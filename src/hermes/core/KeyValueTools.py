import hashlib
import datetime
from warnings import deprecated

from hermes.core.KeyValues import MessageValue, MessageBoxValue, message_key
from hermes.crypt.Crypt import Crypt


class KeyValueTools:
    def __init__(self):
        self._crypt = Crypt()

    def create_message(self, msg: str, sender: str, receiver: str, remote_public_key: str) -> (int, MessageValue):
        '''
        Create a message key, value pair.
        '''
        timestamp = datetime.datetime.now().timestamp()

        enc_msg, wrap_sender, wrap_receiver = self._crypt.encrypt_message_with_key_wrapping(msg, remote_public_key)

        wrapped_keys = [wrap_sender, wrap_receiver]

        return_msg = MessageValue(sender, receiver, enc_msg, str(timestamp), wrapped_keys, "message")

        msg_key = message_key(sender, receiver)

        return  msg_key, return_msg

    def read_message(self, msg: MessageValue, our_nick: str) -> str:
        enc_message = msg.encrypted_message

        #Get the correct wrapped key based on if we are the sender or receiver
        wrapped_key = msg.wrapped_keys[0] if msg.sender == our_nick else msg.wrapped_keys[1]

        return self._crypt.decrypt_message_with_key_wrapping(enc_message, wrapped_key)

    def update_message_box(self, msg: MessageValue, msg_box: MessageBoxValue) -> MessageBoxValue:
        key = message_key(msg.sender, msg.receiver)
        msg_box.message_keys.append(key)
        return msg_box

    def public_key(self):
        return self._crypt.get_public_key()


