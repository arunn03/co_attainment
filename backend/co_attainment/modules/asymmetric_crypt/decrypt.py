import base64
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

def decrypt_message(receiver_private_key, sender_public_key, encrypted_data):
    # Decrypt the symmetric key with the receiver's private key
    encrypted_symmetric_key = base64.b64decode(encrypted_data['encrypted_symmetric_key'])
    symmetric_key = receiver_private_key.decrypt(
        encrypted_symmetric_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    # Decrypt the message with AES
    iv = base64.b64decode(encrypted_data['iv'])
    encrypted_message = base64.b64decode(encrypted_data['encrypted_message'])
    cipher = Cipher(algorithms.AES(symmetric_key), modes.CFB(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    decrypted_message = decryptor.update(encrypted_message) + decryptor.finalize()

    # Verify the signature
    signed_message = base64.b64decode(encrypted_data['signed_message'])
    sender_public_key.verify(
        signed_message,
        decrypted_message,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )

    return decrypted_message.decode()