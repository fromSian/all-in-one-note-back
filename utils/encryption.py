from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from base64 import b64encode, b64decode
import os

class RSAEncryption:
    PUBLIC_KEY = None
    PRIVATE_KEY = None

    def encrypt(self, text):
        if self.PUBLIC_KEY is None:
            self.PUBLIC_KEY = self._get_public_key()

        public_key = RSA.importKey(self.PUBLIC_KEY)
        cipher = PKCS1_OAEP.new(public_key)
        encrypted_text = cipher.encrypt(text.encode("utf-8"))
        return b64encode(encrypted_text)

    def decrypt(self, text):
        print(text, self._get_private_key())
        if self.PRIVATE_KEY is None:
            self.PRIVATE_KEY = self._get_private_key()
        private_key = RSA.importKey(self.PRIVATE_KEY)
        cipher = PKCS1_OAEP.new(private_key)
        decrypted_text = cipher.decrypt(b64decode(text))
        return decrypted_text

    def _get_public_key(self):
        pub = os.environ.get("PUBLIC_KEY")
        return pub

    def _get_private_key(self):
        pri = os.environ.get("PRIVATE_KEY")
        return pri
