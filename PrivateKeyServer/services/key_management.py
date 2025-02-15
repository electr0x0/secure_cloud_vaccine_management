# app/key_management.py
from sqlalchemy.orm import Session
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
import base64
from core.models.models import UserKey
from cryptography.hazmat.primitives.asymmetric import x25519, ed25519
from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305
from config import ENCRYPTION_METHOD
import os

def generate_rsa_key_pair():
    
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )
    public_key = private_key.public_key()
    
    
    private_key_pem = private_key.private_bytes(  # Serialize keys to PEM format
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    public_key_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    
    return private_key_pem, public_key_pem

def generate_key_pair():
    """Factory function that generates key pair based on configured method"""
    if ENCRYPTION_METHOD == "X25519":
        return generate_x25519_key_pair()
    return generate_rsa_key_pair()

def generate_x25519_key_pair():
    """Generates X25519 key pair with Ed25519 for signatures"""
    # Generate X25519 keys for encryption
    private_key = x25519.X25519PrivateKey.generate()
    public_key = private_key.public_key()
    
    # Generate Ed25519 keys for signatures
    signing_key = ed25519.Ed25519PrivateKey.generate()
    verify_key = signing_key.public_key()
    
    # Serialize keys
    private_bytes = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    public_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    
    # Add signature keys to the bundle
    signing_bytes = signing_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    verify_bytes = verify_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    
    # Combine the keys
    private_key_bundle = private_bytes + b"\n" + signing_bytes
    public_key_bundle = public_bytes + b"\n" + verify_bytes
    
    return private_key_bundle, public_key_bundle

def store_user_key_pair(db: Session, user_email: str):
    """Remains unchanged, uses the factory function"""
    private_key_pem, public_key_pem = generate_key_pair()
    private_key_encoded = base64.b64encode(private_key_pem).decode('utf-8')
    public_key_encoded = base64.b64encode(public_key_pem).decode('utf-8')
    
    db_key = UserKey(user_email=user_email, public_key=public_key_encoded, private_key=private_key_encoded)
    db.add(db_key)
    db.commit()
    db.refresh(db_key)
    
    return public_key_encoded

def decrypt_data(db: Session, user_email: str, encrypted_data: str) -> str:
    user_key = db.query(UserKey).filter(UserKey.user_email == user_email).first()
    if not user_key:
        raise ValueError("User not found")

    private_key_bundle = base64.b64decode(user_key.private_key)
    
    if ENCRYPTION_METHOD == "X25519":
        return decrypt_x25519(private_key_bundle, encrypted_data)
    return decrypt_rsa(private_key_bundle, encrypted_data)

def decrypt_x25519(private_key_bundle: bytes, encrypted_data: str) -> str:
    try:
        # Split the bundle to get the encryption key
        private_key_parts = private_key_bundle.split(b"-----BEGIN")
        private_key_pem = b"-----BEGIN" + private_key_parts[1].split(b"-----BEGIN")[0]
        
        # Load the private key
        private_key = serialization.load_pem_private_key(
            private_key_pem,
            password=None
        )
        
        if not isinstance(private_key, x25519.X25519PrivateKey):
            raise ValueError("Invalid key type. Expected X25519 private key.")
        
        # Decode the encrypted data
        encrypted_bytes = base64.b64decode(encrypted_data)
        
        # In X25519, we expect the encrypted data to be in format:
        # [ephemeral_pub_key(32) | nonce(12) | ciphertext | tag(16)]
        if len(encrypted_bytes) < 60:  # Minimum length check (32 + 12 + 16)
            raise ValueError("Encrypted data too short")
            
        ephemeral_pub_bytes = encrypted_bytes[:32]
        nonce = encrypted_bytes[32:44]
        ciphertext_with_tag = encrypted_bytes[44:]  # Keep ciphertext and tag together
        
        # Load the ephemeral public key from raw bytes
        try:
            peer_public_key = x25519.X25519PublicKey.from_public_bytes(ephemeral_pub_bytes)
        except Exception as e:
            raise ValueError(f"Invalid ephemeral public key: {str(e)}")
        
        # Perform key agreement
        shared_key = private_key.exchange(peer_public_key)
        
        # Decrypt using ChaCha20Poly1305
        chacha = ChaCha20Poly1305(shared_key)
        try:
            decrypted_data = chacha.decrypt(nonce, ciphertext_with_tag, None)
        except Exception as e:
            raise ValueError(f"Decryption failed: {str(e)}")
        
        return decrypted_data.decode('utf-8')
        
    except Exception as e:
        raise ValueError(f"Decryption error: {str(e)}")

def decrypt_rsa(private_key_pem: bytes, encrypted_data: str) -> str:
    """Existing RSA decryption logic"""
    private_key = serialization.load_pem_private_key(
        private_key_pem,
        password=None
    )
    
    encrypted_data_bytes = base64.b64decode(encrypted_data)
    decrypted_data = private_key.decrypt(
        encrypted_data_bytes,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    
    return decrypted_data.decode("utf-8")
