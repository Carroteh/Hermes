from base64 import b64encode
from warnings import deprecated

import nacl.public
import base64
import nacl.utils
from nacl.secret import SecretBox
from nacl.public import SealedBox


class Crypt:
    '''
    Class used for cryptography functionality within Hermes, includes generating
    public/private key pairs and encrypting/decrypting messages using NaCl
    '''
    def __init__(self):
        # Key Pair
        self._priv_key = nacl.public.PrivateKey.generate()
        self._pub_key = self._priv_key.public_key

    def get_public_key(self) -> bytes:
        return self._pub_key

    def encrypt_message_with_key_wrapping(self, message : str, remote_public_key : str) -> (str, str, str):
        # Decode the key from a string
        pk = nacl.public.PublicKey(self.b64decode(remote_public_key))

        # Create a symmetric key to encrypt the message
        symmetric_key = nacl.utils.random(SecretBox.KEY_SIZE)
        box = SecretBox(symmetric_key)

        # Encrypt message with secret key
        encrypted_message = box.encrypt(message.encode())

        # Wrap symmetric keys for the users
        sealed_receiver = SealedBox(pk)
        # Assuming this instance is sending
        sealed_sender = SealedBox(self._pub_key)

        wrap_receiver = sealed_receiver.encrypt(symmetric_key)
        wrap_sender = sealed_sender.encrypt(symmetric_key)

        return self.b64encode(encrypted_message), self.b64encode(wrap_sender), self.b64encode(wrap_receiver)

    def decrypt_message_with_key_wrapping(self, message: str, wrapped: str) -> str:
        # Decode the key from a string
        symmetric_key = self.b64decode(wrapped)

        sealed_box = SealedBox(self._priv_key)
        unwrapped_key = sealed_box.decrypt(symmetric_key)

        box = SecretBox(unwrapped_key)
        decrypted_message = box.decrypt(self.b64decode(message))

        return decrypted_message.decode()

    def b64encode(self, data: bytes) -> str:
        return base64.b64encode(data).decode('utf-8')

    def b64decode(self, data: str) -> bytes:
        return base64.b64decode(data.encode('utf-8'))

    def encrypt_message(self, message : str, remote_public_key : bytes) -> bytes:
        box = nacl.public.Box(self._priv_key, remote_public_key)
        nonce = nacl.utils.random(nacl.public.Box.NONCE_SIZE)
        cipher_text = box.encrypt(message.encode(), nonce)
        return cipher_text

    def decrypt_message(self, message : bytes, remote_public_key : bytes) -> str:
        box = nacl.public.Box(self._priv_key, remote_public_key)
        decrypted = box.decrypt(message)
        return decrypted.decode()


