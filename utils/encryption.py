from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
from base64 import b64encode, b64decode

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes

import os


class RSAEncryption:
    PUBLIC_KEY = None
    PRIVATE_KEY = None

    def __init__(self) -> None:
        if self.PRIVATE_KEY is None:
            self.PRIVATE_KEY = self._get_private_key()

        if self.PUBLIC_KEY is None:
            self.PUBLIC_KEY = self._get_public_key()

    def encrypt(self, text):
        public_key = RSA.importKey(self.PUBLIC_KEY)
        cipher = PKCS1_v1_5.new(public_key)
        encrypted_text = cipher.encrypt(text.encode("utf-8"))
        print(encrypted_text)
        return b64encode(encrypted_text)

    def decrypt(self, text):
        private_key = RSA.importKey(self.PRIVATE_KEY)
        cipher = PKCS1_v1_5.new(private_key)
        decrypted_text = cipher.decrypt(b64decode(text), get_random_bytes(32))
        # decrypted_text = cipher.decrypt(text)
        print(text, decrypted_text)
        return decrypted_text

    def _get_public_key(self):
        pub = os.environ.get("PUBLIC_KEY")
        return pub

    def _get_private_key(self):
        pri = os.environ.get("PRIVATE_KEY")
        return pri


class AESEncryption:

    Key: bytes

    def __init__(self):
        self.Key = str.encode(os.environ.get("AES_KEY", ""))

    def encrypt(self, text):
        text = bytes(text, "utf-8")
        iv = get_random_bytes(AES.block_size)
        # Create an AES cipher object with the key and AES.MODE_CBC mode
        cipher = AES.new(self.Key, AES.MODE_CBC, iv)
        # Pad the plaintext and encrypt it
        ciphertext = cipher.encrypt(pad(text, AES.block_size))
        # Concatenate the IV and ciphertext
        encrypted_data = iv + ciphertext
        return encrypted_data.hex()

    def decrypt(self, text):
        ciphertext = bytes.fromhex(text)
        iv = ciphertext[: AES.block_size]
        # Create an AES cipher object with the key, AES.MODE_CBC mode, and the extracted IV
        cipher = AES.new(self.Key, AES.MODE_CBC, iv)
        # Decrypt the ciphertext and remove the padding
        decrypted_data = unpad(
            cipher.decrypt(ciphertext[AES.block_size :]), AES.block_size
        )
        return decrypted_data.decode("utf-8")
