from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from database import Base

class UserKey(Base):
    __tablename__ = "user_keys"
    id = Column(Integer, primary_key=True, index=True)
    user_email = Column(String(255), unique=True, index=True)
    public_key = Column(Text)
    private_key = Column(Text)
    created_at = Column(DateTime, default=func.now())
