from sqlalchemy import Column, Integer, String, Date, ForeignKey, Boolean, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.types import JSON
from core.database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(255))
    last_name = Column(String(255))
    email = Column(String(255), unique=True, index=True)
    user_type = Column(String(50))  # patient, vaccinator, admin
    identity_type = Column(String(50))  # national_id, passport, etc.
    identity_number = Column(Text)  # Encrypted
    phone_number = Column(Text, nullable=True)  # Encrypted
    medical_conditions = Column(Text, nullable=True)  # Encrypted JSON
    dob = Column(Date)
    hashed_password = Column(String(255))
    public_key = Column(Text)

class VaccinationType(Base):
    __tablename__ = "vaccine_types"
    id = Column(Integer, primary_key=True, index=True)
    vaccine_name = Column(String(255))
    vaccine_code = Column(String(50), unique=True, index=True)
    max_doses = Column(Integer)
    
    # Relationship to vaccination history
    vaccinations = relationship("VaccinationHistory", back_populates="vaccine_type")

class VaccinationHistory(Base):
    __tablename__ = "vaccination_history"
    id = Column(Integer, primary_key=True, index=True)
    user_email = Column(String(255), ForeignKey("users.email"))
    vaccine_type_id = Column(Integer, ForeignKey("vaccine_types.id"))
    dose_number = Column(Integer)
    vaccination_date = Column(Date)
    vaccinator_email = Column(String(255), ForeignKey("users.email"))
    notes = Column(Text, nullable=True)
    
    is_taken = Column(Boolean, default=False)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_email])
    vaccine_type = relationship("VaccinationType", back_populates="vaccinations")
    vaccinator = relationship("User", foreign_keys=[vaccinator_email])

    __table_args__ = (
        UniqueConstraint('user_email', 'vaccine_type_id', 'dose_number', name='_user_vaccine_dose_unique'),
    )