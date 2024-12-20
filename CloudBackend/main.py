import base64
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
import models, schemas, auth
from pydantic import EmailStr
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from encryption import encrypt_with_public_key
from config import KEYSERVER
from sqlalchemy import and_, func, extract
from typing import List
from utils import validate_identity
from datetime import datetime
import os
import requests
import json
import config
from prometheus_fastapi_instrumentator import Instrumentator
from prometheus_client import Counter, Histogram, Gauge
from functools import wraps
import time

app = FastAPI()

Instrumentator().instrument(app).expose(app)

# Add custom metrics
encryption_duration = Histogram('encryption_duration_seconds', 'Time spent encrypting data')
encryption_requests = Counter('encryption_requests_total', 'Total encryption requests', ['status'])
key_server_latency = Histogram('key_server_latency_seconds', 'Key server response time')

origins = [
    config.FRONTEND_URL
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def seed_vaccine_types(db: Session):
    vaccine_types = [
        {
            "vaccine_name": "Bacillus Calmette-Guérin (BCG)",
            "vaccine_code": "BCG",
            "max_doses": 5,
        },
        {
            "vaccine_name": "Pentavalent (DPT, Hepatitis B, Hib)",
            "vaccine_code": "PENTAVALENT",
            "max_doses": 5,
        },
        {"vaccine_name": "Oral Polio Vaccine", "vaccine_code": "OPV", "max_doses": 5},
        {
            "vaccine_name": "Pneumococcal Conjugate Vaccine",
            "vaccine_code": "PCV",
            "max_doses": 5,
        },
        {
            "vaccine_name": "Inactivated Polio Vaccine",
            "vaccine_code": "IPV",
            "max_doses": 5,
        },
        {
            "vaccine_name": "Measles and Rubella Vaccine",
            "vaccine_code": "MR",
            "max_doses": 5,
        },
    ]

    for vaccine in vaccine_types:
        existing = (
            db.query(models.VaccinationType)
            .filter_by(vaccine_code=vaccine["vaccine_code"])
            .first()
        )
        if not existing:
            db_vaccine = models.VaccinationType(**vaccine)
            db.add(db_vaccine)

    db.commit()


# Create tables
Base.metadata.create_all(bind=engine)


# Dependency to get the DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Signup route
@app.post("/register", response_model=schemas.UserResponse)
async def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    try:
        # First validate identity number format
        if not validate_identity(user.identity_type, user.identity_number):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid {user.identity_type} format"
            )

        # Check if user already exists
        if db.query(models.User).filter(models.User.email == user.email).first():
            raise HTTPException(
                status_code=400,
                detail="Email already registered"
            )

        # Generate key pair from private key server
        start_time = time.time()
        try:
            key_response = requests.post(
                f"{KEYSERVER}/generate-key-pair",
                params={"user_email": user.email}
            )
            key_server_latency.observe(time.time() - start_time)
            
            if key_response.status_code != 200:
                encryption_requests.labels(status="error").inc()
                raise HTTPException(
                    status_code=500,
                    detail="Failed to generate encryption keys"
                )
            public_key = key_response.json()["encoded_public_key"]
            encryption_requests.labels(status="success").inc()
        except Exception as e:
            encryption_requests.labels(status="error").inc()
            raise HTTPException(
                status_code=500,
                detail="Key server communication failed"
            )

        # Now encrypt sensitive data with the received public key
        start_encrypt = time.time()
        encrypted_identity = encrypt_with_public_key(public_key, user.identity_number)
        encrypted_phone = encrypt_with_public_key(public_key, user.phone_number) if user.phone_number else None
        
        # Encrypt medical conditions if they exist
        encrypted_medical_conditions = None
        if user.medical_conditions:
            medical_conditions_json = [condition.dict() for condition in user.medical_conditions]
            medical_conditions_str = json.dumps(medical_conditions_json)
            encrypted_medical_conditions = encrypt_with_public_key(public_key, medical_conditions_str)
        
        encryption_duration.observe(time.time() - start_encrypt)

        # Create user with encrypted data
        db_user = models.User(
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email,
            user_type=user.user_type,
            identity_type=user.identity_type,
            identity_number=encrypted_identity,
            phone_number=encrypted_phone,
            medical_conditions=encrypted_medical_conditions,
            dob=user.dob,
            hashed_password=auth.get_password_hash(user.password),
            public_key=public_key
        )

        db.add(db_user)
        db.commit()
        db.refresh(db_user)

        return {"success": True, "message": "User registered successfully"}

    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# Login route
@app.post("/login")
def login(loginInfo: schemas.UserLogin, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == loginInfo.email).first()
    if not user or not auth.verify_password(loginInfo.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )

    # Generate JWT token
    access_token = auth.create_access_token(data={"sub": user.email})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "userGroup": user.user_type,
        "userName": user.first_name + user.last_name,
    }


@app.get("/api/user/info", response_model=schemas.UserInfoResponse)
async def get_user_info(
    token: str,
    db: Session = Depends(get_db)
):
    try:
        # Current user's information is already verified through the token
        db_user = auth.get_current_user(token=token, db=db)

        # Decrypt sensitive information
        start_time = time.time()
        
        # Decrypt identity number
        json = {"data": db_user.identity_number, "token": token}
        identity_response = requests.post(url=f"{KEYSERVER}/decrypt-data", json=json)
        
        # Decrypt phone number if exists
        phone_number = None
        if db_user.phone_number:
            json = {"data": db_user.phone_number, "token": token}
            phone_response = requests.post(url=f"{KEYSERVER}/decrypt-data", json=json)
            phone_number = phone_response.json()["decrypted_data"]
        
        # Decrypt medical conditions if exists
        medical_conditions = []
        if db_user.medical_conditions:
            json = {"data": db_user.medical_conditions, "token": token}
            medical_response = requests.post(url=f"{KEYSERVER}/decrypt-data", json=json)
            medical_conditions = medical_response.json()["decrypted_data"]
        
        # Record total decryption time
        key_server_latency.observe(time.time() - start_time)
        encryption_requests.labels(status="success").inc()
        
        return schemas.UserInfoResponse(
            first_name=db_user.first_name,
            last_name=db_user.last_name,
            email=db_user.email,
            user_type=db_user.user_type,
            identity_type=db_user.identity_type,
            identity_number=identity_response.json()["decrypted_data"],
            phone_number=phone_number,
            medical_conditions=medical_conditions,
            dob=db_user.dob,
            public_key=db_user.public_key
        )
        
    except Exception as e:
        encryption_requests.labels(status="error").inc()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@app.put("/api/user/update", response_model=schemas.UserInfoResponse)
async def update_user_info(
    user_update: schemas.UserUpdate,
    db: Session = Depends(get_db)
):
    try:
        # Current user's information is already verified through the token
        db_user = auth.get_current_user(token=user_update.token, db=db)
        
        # Update basic information
        db_user.first_name = user_update.first_name
        db_user.last_name = user_update.last_name
        db_user.dob = user_update.dob
        
        # Update and encrypt identity number if provided
        if user_update.identity_number:
            if not validate_identity(user_update.identity_type, user_update.identity_number):
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid {user_update.identity_type} format"
                )
            encrypted_identity = encrypt_with_public_key(
                db_user.public_key, 
                user_update.identity_number
            )
            db_user.identity_number = encrypted_identity
            db_user.identity_type = user_update.identity_type
            
        # Update and encrypt phone number if provided
        if user_update.phone_number:
            encrypted_phone = encrypt_with_public_key(
                db_user.public_key, 
                user_update.phone_number
            )
            db_user.phone_number = encrypted_phone
            
        # Update and encrypt medical conditions if provided
        if user_update.medical_conditions:
            medical_conditions_json = json.dumps(user_update.medical_conditions)
            encrypted_medical_conditions = encrypt_with_public_key(
                db_user.public_key, 
                medical_conditions_json
            )
            db_user.medical_conditions = encrypted_medical_conditions
            
        db.commit()
        db.refresh(db_user)
        
   
    
        
        return schemas.UserInfoResponse(
            first_name=db_user.first_name,
            last_name=db_user.last_name,
            email=db_user.email,
            user_type=db_user.user_type,
            identity_type=db_user.identity_type,
            identity_number=db_user.identity_number,
            phone_number=db_user.phone_number,
            medical_conditions=db_user.medical_conditions,
            dob=db_user.dob,
            public_key=db_user.public_key
        )
        
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@app.post("/api/get-vaccination-history/by-jwt/", response_model=schemas.VaccinationFullHistoryResponse)
def get_vaccination_history_by_jwt(jwt: schemas.TokenInput, db: Session = Depends(get_db)):
    user = auth.get_current_user(token=jwt.token, db=db)
    
    return get_vaccination_history(email=user.email, db=db)

@app.get(
    "/api/vaccination-history", response_model=schemas.VaccinationFullHistoryResponse
)
def get_vaccination_history(email: str, db: Session = Depends(get_db)):
    # First, verify the email exists in the users table
    user = db.query(models.User).filter(models.User.email == email).first()

    # If user not found, raise an HTTP exception
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User with this email not found",
        )

    # Prepare user info
    user_info = {
        "user_name": f"{user.first_name} {user.last_name}",
        "user_email": user.email,
    }

    # Get all vaccine types
    vaccine_types = db.query(models.VaccinationType).all()

    # Prepare vaccination history
    vaccination_history = []

    for vaccine_type in vaccine_types:
        # Fetch vaccination entries for this user and vaccine type
        existing_doses = (
            db.query(models.VaccinationHistory)
            .filter(
                and_(
                    models.VaccinationHistory.user_email == email,
                    models.VaccinationHistory.vaccine_type_id == vaccine_type.id,
                )
            )
            .order_by(models.VaccinationHistory.dose_number)
            .all()
        )

        # Create a complete dose list with existing entries and empty entries
        dose_data = []
        for i in range(1, vaccine_type.max_doses + 1):
            # Try to find an existing dose for this number
            existing_dose = next(
                (dose for dose in existing_doses if dose.dose_number == i), None
            )

            if existing_dose:
                # If dose exists, use its data
                dose_data.append(
                    {
                        "dose_number": existing_dose.dose_number,
                        "vaccination_date": existing_dose.vaccination_date,
                        "is_taken": existing_dose.is_taken,
                    }
                )
            else:
                # If no dose exists, create an empty entry
                dose_data.append(
                    {
                        "dose_number": i,
                        "vaccination_date": None,
                        "is_taken": False,
                    }
                )

        vaccination_history.append(
            {
                "vaccine_code": vaccine_type.vaccine_code,
                "vaccine_name": vaccine_type.vaccine_name,
                "doses": dose_data,
            }
        )

    # Return the full response structure
    return {"user_info": user_info, "vaccination_history": vaccination_history}


@app.post("/api/vaccination-history")
def update_vaccination_history(
    payload: schemas.VaccinationEntryCreate,
    db: Session = Depends(get_db),
):
    # Verify vaccinator authentication and authorization
    try:
        current_user = auth.get_current_user(token=payload.token, db=db)

        # Check if vaccinator has the required user group (group ID 2)
        if current_user.user_type != 2:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only authorized healthcare workers can update vaccination records",
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed"
        )

    # Check if recipient user exists
    recipient_user = (
        db.query(models.User).filter(models.User.email == payload.email).first()
    )

    if not recipient_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Recipient user not found"
        )

    # Find the vaccine type
    vaccine_type = (
        db.query(models.VaccinationType)
        .filter_by(vaccine_code=payload.vaccine_code)
        .first()
    )

    if not vaccine_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Vaccine type not found"
        )

    # Check if dose number is valid
    if payload.dose_number < 1 or payload.dose_number > vaccine_type.max_doses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid dose number"
        )

    # Validate previous doses for this vaccine type
    if payload.dose_number > 1 and payload.is_taken:
        # Check all previous doses
        previous_doses = (
            db.query(models.VaccinationHistory)
            .filter(
                and_(
                    models.VaccinationHistory.user_email == payload.email,
                    models.VaccinationHistory.vaccine_type_id == vaccine_type.id,
                    models.VaccinationHistory.dose_number < payload.dose_number,
                )
            )
            .order_by(models.VaccinationHistory.dose_number)
            .all()
        )

        # If there are fewer previous doses than expected, or any previous dose is not taken
        if len(previous_doses) < payload.dose_number - 1 or any(
            not dose.is_taken for dose in previous_doses
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot add dose {payload.dose_number} before completing previous doses",
            )

    # Find existing entry or create new
    existing_entry = (
        db.query(models.VaccinationHistory)
        .filter(
            and_(
                models.VaccinationHistory.user_email == payload.email,
                models.VaccinationHistory.vaccine_type_id == vaccine_type.id,
                models.VaccinationHistory.dose_number == payload.dose_number,
            )
        )
        .first()
    )

    if existing_entry:
        # Update existing entry
        existing_entry.vaccination_date = payload.vaccination_date
        existing_entry.is_taken = payload.is_taken
    else:
        # Create new entry
        new_entry = models.VaccinationHistory(
            user_email=payload.email,
            vaccine_type_id=vaccine_type.id,
            dose_number=payload.dose_number,
            vaccination_date=payload.vaccination_date,
            is_taken=payload.is_taken,
        )
        db.add(new_entry)

    db.commit()
    db.refresh(existing_entry) if existing_entry else None

    return {"message": "Vaccination history updated successfully"}


@app.on_event("startup")
def startup_event():
    db = SessionLocal()
    try:
        seed_vaccine_types(db)
    finally:
        db.close()


@app.post("/api/vaccination-stats")
def get_vaccination_stats(jwt: schemas.TokenInput, db: Session = Depends(get_db)):
    try:
        # Verify user and check if they're a healthcare worker (user_type = 2)
        current_user = auth.get_current_user(token=jwt.token, db=db)
        if current_user.user_type != 2:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only healthcare workers can access statistics"
            )

        # Get current year
        current_year = datetime.now().year

        # Query monthly vaccination counts
        monthly_stats = (
            db.query(
                extract('month', models.VaccinationHistory.vaccination_date).label('month'),
                func.count().label('count')
            )
            .filter(
                extract('year', models.VaccinationHistory.vaccination_date) == current_year,
                models.VaccinationHistory.is_taken == True
            )
            .group_by(extract('month', models.VaccinationHistory.vaccination_date))
            .all()
        )

        # Create a dictionary with all months initialized to 0
        month_names = ['January', 'February', 'March', 'April', 'May', 'June', 
                      'July', 'August', 'September', 'October', 'November', 'December']
        monthly_data = {month: 0 for month in month_names}
        
        # Update with actual values
        for stat in monthly_stats:
            monthly_data[month_names[stat.month-1]] = stat.count

        # Convert to list format
        monthly_data = [
            {"month": month, "vaccinations": count}
            for month, count in monthly_data.items()
        ]

        # Query vaccine type distribution
        vaccine_stats = (
            db.query(
                models.VaccinationType.vaccine_name,
                func.count().label('count')
            )
            .join(models.VaccinationHistory)
            .filter(models.VaccinationHistory.is_taken == True)
            .group_by(models.VaccinationType.vaccine_name)
            .all()
        )

        vaccine_distribution = [
            {"name": stat.vaccine_name, "value": stat.count}
            for stat in vaccine_stats
        ]

        return {
            "monthly_data": monthly_data,
            "vaccine_distribution": vaccine_distribution
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )



if __name__ == "__main__":
    env = config.ENVIRONMENT
    
    # Common settings
    config_dict = {
        "host": config.SERVER_HOST,
        "port": int(config.SERVER_PORT),
        "access_log": True
    }
    
    if env == "production":
        # Production settings
        config_dict.update({
            "reload": False,
            "workers": 4,
            "proxy_headers": True,
            "forwarded_allow_ips": '*'
        })
        # Disable Swagger UI and ReDoc in production
        app.docs_url = None
        app.redoc_url = None
    else:
        # Development settings 
        config_dict.update({
            "reload": True,
            "workers": 1,
            "proxy_headers": False
        })

    uvicorn.run("main:app", **config_dict)