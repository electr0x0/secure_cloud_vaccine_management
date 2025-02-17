from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
import json
import time
import requests
from prometheus_client import Counter, Histogram
from core.metrics import ENCRYPTION_TIME, ENCRYPTION_REQUESTS, KEY_SERVER_LATENCY, CONCURRENT_OPERATIONS

from core.database import get_db
from core import auth
from core.models.models import User
from core.models import schemas
from services.encryption import encrypt_with_public_key
from config import KEYSERVER
from core.utils import validate_identity

router = APIRouter()

@router.post("/register", response_model=schemas.UserResponse)
async def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    CONCURRENT_OPERATIONS.labels(operation_type="encryption").inc()
    start_time = time.time()
    try:
        # First validate identity number format
        if not validate_identity(user.identity_type, user.identity_number):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid {user.identity_type} format"
            )

        # Check if user already exists
        if db.query(User).filter(User.email == user.email).first():
            raise HTTPException(
                status_code=400,
                detail="Email already registered"
            )

        # Generate key pair from private key server
        key_server_start = time.time()
        key_response = requests.post(
            f"{KEYSERVER}/generate-key-pair",
            params={"user_email": user.email}
        )
        KEY_SERVER_LATENCY.labels(operation_type="key_generation").observe(
            time.time() - key_server_start
        )
        
        if key_response.status_code != 200:
            raise HTTPException(
                status_code=500,
                detail="Failed to generate encryption keys"
            )
        public_key = key_response.json()["encoded_public_key"]
        
        # Now encrypt sensitive data with the received public key
        encrypted_identity = encrypt_with_public_key(public_key, user.identity_number)
        encrypted_phone = encrypt_with_public_key(public_key, user.phone_number) if user.phone_number else None
        
        # Encrypt medical conditions if they exist
        encrypted_medical_conditions = None
        if user.medical_conditions:
            medical_conditions_json = json.dumps([mc.dict() for mc in user.medical_conditions])
            encrypted_medical_conditions = encrypt_with_public_key(public_key, medical_conditions_json)

        # Create user with encrypted data
        db_user = User(
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

        ENCRYPTION_REQUESTS.labels(
            operation_type="registration",
            status="success"
        ).inc()
        
        return {"success": True, "message": "User registered successfully"}
    except Exception as e:
        ENCRYPTION_REQUESTS.labels(
            operation_type="registration",
            status="error"
        ).inc()
        raise
    finally:
        ENCRYPTION_TIME.labels(
            operation_type="registration",
            status="success" if "success" in locals() else "error"
        ).observe(time.time() - start_time)
        CONCURRENT_OPERATIONS.labels(operation_type="encryption").dec()

@router.post("/login")
def login(login_info: schemas.UserLogin, db: Session = Depends(get_db)):
    try:
        user = db.query(User).filter(User.email == login_info.email).first()
        if not user or not auth.verify_password(login_info.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
            )

        # Generate JWT token
        return {"access_token": auth.create_access_token(user.email), "userName": f"{user.first_name} {user.last_name}", "userGroup": user.user_type}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))