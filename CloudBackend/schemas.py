from pydantic import BaseModel, EmailStr, Field
from datetime import date
from typing import Optional

class UserCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    user_type: str
    national_id: str
    dob: str  # Could be date field, keeping as string for simplicity
    password: str = Field(..., min_length=8)
    
class UserLogin(BaseModel):
    email: EmailStr
    password : str

class UserResponse(BaseModel):
    message: str
    
    class Config:
        from_attributes = True
        
        

class TokenInput(BaseModel):
    token: str


class UserInfoResponse(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    user_type: int
    national_id: str
    dob: date
    public_key: str