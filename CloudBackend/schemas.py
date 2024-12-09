from pydantic import BaseModel, EmailStr, Field
from datetime import date
from typing import Optional, List

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
    
