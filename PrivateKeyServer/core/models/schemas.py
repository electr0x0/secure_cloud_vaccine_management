# app/schemas.py
from pydantic import BaseModel

class KeyRequest(BaseModel):
    user_email: str  # Email of the user whose data needs to be decrypted
    data: str  # Encrypted data to be decrypted
    token: str  # JWT token for authentication

class KeyResponse(BaseModel):
    encoded_public_key: str  # For public key or decrypted data
    
    
class DataDecryptResponse(BaseModel):
    decrypted_data: str