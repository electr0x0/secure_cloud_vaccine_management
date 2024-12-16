from pydantic import BaseModel, EmailStr, Field
from datetime import date
from typing import Optional, List, Dict, Any
from enum import Enum

class IdentityType(str, Enum):
    NID = "nid"
    BRN = "brn"
    PASSPORT = "passport"

class MedicalCondition(BaseModel):
    condition_name: str
    details: str
    severity: str
    diagnosed_date: Optional[str]

class UserCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    user_type: str
    identity_type: IdentityType
    identity_number: str
    phone_number: Optional[str]
    medical_conditions: Optional[List[MedicalCondition]]
    dob: str
    password: str = Field(..., min_length=8)
    
    class Config:
        use_enum_values = True
        
        

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
    email: str
    user_type: int
    identity_type: str
    identity_number: str
    phone_number: Optional[str] = None
    medical_conditions: Optional[Any]
    public_key: str

class UserUpdate(BaseModel):
    first_name: str
    last_name: str
    identity_type: Optional[str] = None
    identity_number: Optional[str] = None
    phone_number: Optional[str] = None
    medical_conditions: Optional[Any] = None
    dob: date
    token: str  # For decryption

class VaccinationEntryCreate(BaseModel):
    email: EmailStr
    token: str
    vaccine_code: str = Field(..., description="Unique code for the vaccine")
    dose_number: int = Field(ge=1, le=5, description="Dose number (1-5)")
    vaccination_date: Optional[date] = None
    is_taken: bool = False

class UserInfoResponseNoLogin(BaseModel):
    user_name: str
    user_email: EmailStr

class DoseResponse(BaseModel):
    dose_number: int
    vaccination_date: Optional[date]
    is_taken: bool

class VaccineHistoryItemResponse(BaseModel):
    vaccine_code: str
    vaccine_name: str
    doses: List[DoseResponse]

class VaccinationFullHistoryResponse(BaseModel):
    user_info: UserInfoResponseNoLogin
    vaccination_history: List[VaccineHistoryItemResponse]

class VaccinationHistoryRequest(BaseModel):
    email: EmailStr
    
class UserInfoUpdate(BaseModel):
    token: str
    first_name: str
    last_name: str
    email: EmailStr
    national_id: str
    dob: date
    
    class Config:
        from_attributes = True
        
        
