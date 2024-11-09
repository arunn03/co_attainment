from cryptography.hazmat.primitives import serialization

def load_private_key(private_key_pem_str):
    # Convert the PEM string back to a private key object
    private_key = serialization.load_pem_private_key(
        private_key_pem_str.encode('utf-8'),  # Convert string to bytes
        password=None  # Specify a password if the key is encrypted
    )
    return private_key

def load_public_key(public_key_pem_str):
    # Convert the PEM string back to a public key object
    public_key = serialization.load_pem_public_key(
        public_key_pem_str.encode('utf-8')  # Convert string to bytes
    )
    return public_key