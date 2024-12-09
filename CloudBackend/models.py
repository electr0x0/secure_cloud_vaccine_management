from sqlalchemy import Column, Integer, String, Date, ForeignKey, Boolean, Text, UniqueConstraint
from sqlalchemy.orm import relationship
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

class VaccinationType(Base):
    __tablename__ = "vaccine_types"
    
    id = Column(Integer, primary_key=True, index=True)
    vaccine_name = Column(String(100), nullable=False, unique=True)
    vaccine_code = Column(String(20), nullable=False, unique=True)
    max_doses = Column(Integer, default=5)
    
    # Relationship to vaccination history
    vaccinations = relationship("VaccinationHistory", back_populates="vaccine_type")
    
class VaccinationHistory(Base):
    __tablename__ = "vaccination_histories"
    
    id = Column(Integer, primary_key=True, index=True)
    user_email = Column(String(255), ForeignKey('users.email'), nullable=False)
    vaccine_type_id = Column(Integer, ForeignKey('vaccine_types.id'), nullable=False)
    dose_number = Column(Integer, nullable=False)
    vaccination_date = Column(Date, nullable=True)  # Can be null if not taken
    is_taken = Column(Boolean, default=False)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_email])
    vaccine_type = relationship("VaccinationType", back_populates="vaccinations")

    # Unique constraint to prevent duplicate dose entries
    __table_args__ = (
        # Ensures unique combination of user, vaccine type, and dose number
        UniqueConstraint('user_email', 'vaccine_type_id', 'dose_number', name='_user_vaccine_dose_unique'),
    )