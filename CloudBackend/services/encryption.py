from cryptography.hazmat.primitives.asymmetric import padding, x25519
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305
import base64
import os
from config import ENCRYPTION_METHOD

def encrypt_with_public_key(public_key_pem: str, plaintext: str) -> str:
    """Encrypts data with either RSA or X25519 based on configuration"""
    if ENCRYPTION_METHOD == "X25519":
        return encrypt_x25519(public_key_pem, plaintext)
    return encrypt_rsa(public_key_pem, plaintext)

def encrypt_rsa(public_key_pem: str, plaintext: str) -> str:
    """Original RSA encryption logic"""
    public_key_decode = base64.b64decode(public_key_pem)
    public_key = serialization.load_pem_public_key(public_key_decode)
    
    encrypted_data = public_key.encrypt(
        plaintext.encode(),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    
    return base64.b64encode(encrypted_data).decode('utf-8')

def encrypt_x25519(public_key_pem: str, plaintext: str) -> str:
    """X25519 encryption with ChaCha20Poly1305"""
    try:
        # Decode the base64-encoded PEM public key
        public_key_bundle = base64.b64decode(public_key_pem)
        
        # Split the bundle if it contains multiple keys
        encryption_key_pem = public_key_bundle.split(b"\n-----BEGIN")[0] + b"\n"
        if not encryption_key_pem.startswith(b"-----BEGIN"):
            encryption_key_pem = b"-----BEGIN" + encryption_key_pem
            
        # Load the X25519 public key
        public_key = serialization.load_pem_public_key(encryption_key_pem)
        
        if not isinstance(public_key, x25519.X25519PublicKey):
            raise ValueError("Invalid key type. Expected X25519 public key.")
        
        # Generate ephemeral key pair
        ephemeral_private = x25519.X25519PrivateKey.generate()
        ephemeral_public = ephemeral_private.public_key()
        
        # Perform key agreement
        shared_key = ephemeral_private.exchange(public_key)
        
        # Generate nonce
        nonce = os.urandom(12)
        
        # Encrypt using ChaCha20Poly1305
        chacha = ChaCha20Poly1305(shared_key)
        ciphertext = chacha.encrypt(nonce, plaintext.encode(), None)
        
        # Format: ephemeral_public_key (32) | nonce (12) | ciphertext | tag (16)
        ephemeral_public_bytes = ephemeral_public.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw
        )
        
        # Combine all components
        final_message = ephemeral_public_bytes + nonce + ciphertext
        
        # Encode to base64 for transmission
        return base64.b64encode(final_message).decode('utf-8')
        
    except Exception as e:
        # Add better error handling
        raise ValueError(f"Encryption failed: {str(e)}")

# Test
if __name__ == "__main__":
    val = encrypt_with_public_key("LS0tLS1CRUdJTiBQVUJMSUMgS0VZLS0tLS0KTUlJQklqQU5CZ2txaGtpRzl3MEJBUUVGQUFPQ0FROEFNSUlCQ2dLQ0FRRUF5U0RROFV4SFUzWlMvOVpDNTNUTgpDQ1F1RjJXTWZ0Yk9QcTgrcklwQVVVaDFwTGNheHpxcmN2Umg1SjVDLzFTR2g0b3p6WE0xbXlmRkc0OFZ1ZjdJClR4MXNLVDVDM2ZlZUdSWVd2Q05MTnNRekhXVDNWR1JDSEJRemxQTnNPbUkxRnlpTWI0ODZJM2hoaFNjckpXMk4KR0s3TXcvT1RrWUMvQkh1VkI1cHJzRGljdjVrWVg4VDZ1TUZsblVtYjl5aTdlWUY5cUF1WGVReVNEU3B3dWtIago5dlNaSEZEV2w2RjE2MTNQUk1CYWFSbjZ1eG40S2NOMEowVisyTy9nMDRLNXl4enhxajVacmV6Qi9LVjd6WW5wCjNrZ2dqVmdaN2NFR3l6NUd6Z2hpRGZrRlBMUW5YdEgyNm5QZnIvTEFvcTNBUjlvRjcrUnZ4V2d5ZDFzVU5CUlcKcHdJREFRQUIKLS0tLS1FTkQgUFVCTElDIEtFWS0tLS0tCg==", "4242424")
    
    print(val)
