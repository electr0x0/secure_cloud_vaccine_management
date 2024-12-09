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
from sqlalchemy import and_
from typing import List

import requests

app = FastAPI()

origins = [
    "http://localhost:3000",
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
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Check if email already exists
    db_user = db.query(models.User).filter((models.User.email == user.email)).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = auth.get_password_hash(user.password)

    keyserver_payload = {"user_email": user.email}

    generate_key_pair = requests.post(
        url=f"{KEYSERVER}/generate-key-pair", params=keyserver_payload
    )

    response = generate_key_pair.json()

    public_key = response["encoded_public_key"]

    print(public_key)

    db_user = models.User(
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        user_type=int(user.user_type),
        national_id=encrypt_with_public_key(public_key, user.national_id),
        dob=user.dob,
        hashed_password=hashed_password,
        public_key=public_key,
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return {"message": "successfully registered"}


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


@app.post("/user-info", response_model=schemas.UserInfoResponse)
def get_user_info(token_input: schemas.TokenInput, db: Session = Depends(get_db)):

    user = auth.get_current_user(token=token_input.token, db=db)

    json = {"data": user.national_id, "token": token_input.token}

    response = requests.post(url=f"{KEYSERVER}/decrypt-data", json=json).json()

    if response["decrypted_data"]:
        return schemas.UserInfoResponse(
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email,
            user_type=user.user_type,
            national_id=response["decrypted_data"],
            dob=user.dob,
            public_key=user.public_key,
        )
    else:
        return {"message": "User Authentiation Failed"}


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


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
