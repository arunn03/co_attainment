import os
import base64
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

def encrypt_message(sender_private_key, receiver_public_key, message):

    # Encrypt the message with a symmetric key (AES)
    symmetric_key = os.urandom(32)  # 256-bit key for AES
    iv = os.urandom(16)  # Initialization vector
    cipher = Cipher(algorithms.AES(symmetric_key), modes.CFB(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    encrypted_message = encryptor.update(message.encode()) + encryptor.finalize()

    # Sign the original message with the sender's private key
    signed_message = sender_private_key.sign(
        message.encode(),
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )

    # Encrypt the symmetric key with the receiver's public key
    encrypted_symmetric_key = receiver_public_key.encrypt(
        symmetric_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    return {
        'encrypted_message': base64.b64encode(encrypted_message).decode('utf-8'),
        'encrypted_symmetric_key': base64.b64encode(encrypted_symmetric_key).decode('utf-8'),
        'iv': base64.b64encode(iv).decode('utf-8'),
        'signed_message': base64.b64encode(signed_message).decode('utf-8')
    }