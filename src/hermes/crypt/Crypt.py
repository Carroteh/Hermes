import nacl.public
import nacl.utils

class Crypt:
    def __init__(self):
        # Key Pair
        self._priv_key = nacl.public.PrivateKey.generate()
        self._pub_key = self._priv_key.public_key

    def get_public_key(self) -> bytes:
        return self._pub_key

    def encrypt_message(self, message : str, remote_public_key : bytes) -> bytes:
        box = nacl.public.Box(self._priv_key, remote_public_key)
        nonce = nacl.utils.random(nacl.public.Box.NONCE_SIZE)
        cipher_text = box.encrypt(message.encode(), nonce)
        return cipher_text

    def decrypt_message(self, message : bytes, remote_public_key : bytes) -> str:
        box = nacl.public.Box(self._priv_key, remote_public_key)
        decrypted = box.decrypt(message)
        return decrypted.decode()

