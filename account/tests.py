from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes


def encrypt(plaintext, key):
    # Generate a random initialization vector (IV)
    iv = get_random_bytes(AES.block_size)
    print(AES.block_size)
    # Create an AES cipher object with the key and AES.MODE_CBC mode
    cipher = AES.new(key, AES.MODE_CBC, iv)
    # Pad the plaintext and encrypt it
    ciphertext = cipher.encrypt(pad(plaintext, AES.block_size))
    # Concatenate the IV and ciphertext
    encrypted_data = iv + ciphertext
    return encrypted_data


def decrypt(ciphertext, key):
    # Extract the IV from the ciphertext
    iv = ciphertext[: AES.block_size]
    # Create an AES cipher object with the key, AES.MODE_CBC mode, and the extracted IV
    cipher = AES.new(key, AES.MODE_CBC, iv)
    # Decrypt the ciphertext and remove the padding
    decrypted_data = unpad(cipher.decrypt(ciphertext[AES.block_size :]), AES.block_size)
    return decrypted_data


# Example usage
# Generate a random 256-bit (32-byte) key
# Key-length accepted: 16, 24, and 32 bytes.
# key = get_random_bytes(24)
# print("Key:", key.hex())

key = str.encode("a44dccba16b3c28f27e821a6297711b7")
plaintext = b"a44dccba16b3c28f27e8"
# Encryption
encrypted_data = encrypt(plaintext, key)
print("Encrypted data:", encrypted_data)
# Decryption
decrypted_data = decrypt(encrypted_data, key)
print("Decrypted data:", decrypted_data.decode("utf-8"))

import os


class AESEncryption:

    Key: bytes

    def __init__(self):
        self.Key = str.encode(os.environ.get("AES_KEY", ""))

    def encrypt(self, text):
        text = bytes(text, 'utf-8')
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
