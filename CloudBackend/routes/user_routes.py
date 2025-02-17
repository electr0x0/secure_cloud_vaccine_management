from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import json
import requests
import time

from core.database import get_db
from core.auth import get_current_user
from core.models.models import User
from core.models import schemas
from services.encryption import encrypt_with_public_key
from config import KEYSERVER
from core.metrics import ENCRYPTION_TIME, ENCRYPTION_REQUESTS, KEY_SERVER_LATENCY, CONCURRENT_OPERATIONS

router = APIRouter()

@router.get("/info", response_model=schemas.UserInfoResponse)
async def get_user_info(token: str, db: Session = Depends(get_db)):
    CONCURRENT_OPERATIONS.labels(operation_type="decryption").inc()
    start_time = time.time()
    try:
        # Get user email from token
        user_email = get_current_user(token, db)
        
        # Get user from database using the email string
        user = db.query(User).filter(User.email == user_email).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Get decrypted data from key server
        try:
            start_time = time.time()
            # Decrypt identity number
            identity_response = requests.post(
                f"{KEYSERVER}/decrypt-data",
                json={
                    "user_email": user_email,
                    "token": token,
                    "data": user.identity_number
                }
            )
        
            
            if identity_response.status_code != 200:
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to decrypt identity number: {identity_response.text}"
                )
            decrypted_identity = identity_response.json()["decrypted_data"]

            # Decrypt phone number if exists
            decrypted_phone = None
            if user.phone_number:
                phone_response = requests.post(
                    f"{KEYSERVER}/decrypt-data",
                    json={
                        "user_email": user_email,
                        "token": token,
                        "data": user.phone_number
                    }
                )
                if phone_response.status_code == 200:
                    decrypted_phone = phone_response.json()["decrypted_data"]

            # Decrypt medical conditions if exists
            decrypted_medical_conditions = []
            if user.medical_conditions:
                med_response = requests.post(
                    f"{KEYSERVER}/decrypt-data",
                    json={
                        "user_email": user_email,
                        "token": token,
                        "data": user.medical_conditions
                    }
                )
                if med_response.status_code == 200:
                    decrypted_med_data = med_response.json()["decrypted_data"]
                    decrypted_medical_conditions = json.loads(decrypted_med_data)
                    
            response_time = time.time() - start_time
            KEY_SERVER_LATENCY.labels(operation_type="decryption").observe(response_time)

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to decrypt user data: {str(e)}"
            )

        user_info = schemas.UserInfoResponse(
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email,
            user_type=user.user_type,
            identity_type=user.identity_type,
            identity_number=decrypted_identity,
            phone_number=decrypted_phone,
            medical_conditions=decrypted_medical_conditions,
            dob=user.dob,
            public_key=user.public_key
        )

        ENCRYPTION_REQUESTS.labels(
            operation_type="decryption",
            status="success"
        ).inc()
        return user_info
    except Exception as e:
        ENCRYPTION_REQUESTS.labels(
            operation_type="decryption",
            status="error"
        ).inc()
        raise
    finally:
        ENCRYPTION_TIME.labels(
            operation_type="decryption",
            status="success" if "user_info" in locals() else "error"
        ).observe(time.time() - start_time)
        CONCURRENT_OPERATIONS.labels(operation_type="decryption").dec()

@router.put("/update", response_model=schemas.UserInfoResponse)
async def update_user_info(user_update: schemas.UserUpdate, db: Session = Depends(get_db)):
    try:
        # Get user from database
        user_email = get_current_user(user_update.token, db)
        
        user = db.query(User).filter(User.email == user_email).first()

        # Update non-sensitive fields
        user.first_name = user_update.first_name
        user.last_name = user_update.last_name
        user.dob = user_update.dob

        # Encrypt and update sensitive fields
        if user_update.phone_number:
            encrypted_phone = encrypt_with_public_key(user.public_key, user_update.phone_number)
            user.phone_number = encrypted_phone

        # Update and encrypt medical conditions if provided
        if user_update.medical_conditions:
            medical_conditions_json = json.dumps(user_update.medical_conditions)
            encrypted_medical_conditions = encrypt_with_public_key(
                user.public_key, 
                medical_conditions_json
            )
            user.medical_conditions = encrypted_medical_conditions

        db.commit()
        db.refresh(user)

        # Return updated user info
        return await get_user_info(user_update.token, db)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))