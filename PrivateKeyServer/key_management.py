# app/key_management.py
from sqlalchemy.orm import Session
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
import base64
from models import UserKey

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

def store_user_key_pair(db: Session, user_email: str):
    #Generates and stores RSA key pair for a user, saving only the public key.
    private_key_pem, public_key_pem = generate_rsa_key_pair()
    
    
    private_key_encoded = base64.b64encode(private_key_pem).decode('utf-8')
    public_key_encoded = base64.b64encode(public_key_pem).decode('utf-8')
    
    
    db_key = UserKey(user_email=user_email, public_key=public_key_encoded, private_key=private_key_encoded)
    db.add(db_key)
    db.commit()
    db.refresh(db_key)
    
    return public_key_encoded

def decrypt_data(db: Session, user_email: str, encrypted_data: str) -> str:
    
    
    #Decrypts data for a user using the stored private key.
    user_key = db.query(UserKey).filter(UserKey.user_email == user_email).first()
    if not user_key:
        raise ValueError("User not found")
    

    private_key_pem = base64.b64decode(user_key.private_key)
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
