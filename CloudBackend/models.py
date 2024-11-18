from sqlalchemy import Column, String, Integer, Date, Text
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    user_type = Column(Integer, nullable=False)
    national_id = Column(Text)
    dob = Column(Date, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    
    public_key = Column(Text)