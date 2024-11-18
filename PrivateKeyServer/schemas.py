# app/schemas.py
from pydantic import BaseModel

class KeyRequest(BaseModel):
    data: str  # Encrypted data to be decrypted
    token: str

class KeyResponse(BaseModel):
    encoded_public_key: str  # For public key or decrypted data
    
    
class DataDecryptResponse(BaseModel):
    decrypted_data: str