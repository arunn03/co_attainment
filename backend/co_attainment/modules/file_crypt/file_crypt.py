from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
import base64
import os

def generate_key_and_iv():
    # Generate a 16-byte (128-bit) key and IV
    key = os.urandom(16)  # 128-bit key
    iv = os.urandom(16)   # 128-bit IV
    return key, iv

def encrypt_data(data, key, iv):
    # Pad the data to ensure it's a multiple of 16 bytes
    padder = padding.PKCS7(algorithms.AES.block_size).padder()
    padded_data = padder.update(data.encode()) + padder.finalize()

    # Create AES cipher in CBC mode
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()

    # Encrypt the data
    ciphertext = encryptor.update(padded_data) + encryptor.finalize()

    # Return Base64 encoded IV and ciphertext
    encrypted_data = base64.b64encode(iv + ciphertext).decode('utf-8')
    return encrypted_data
