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
    db_user = db.query(models.User).filter(
        (models.User.email == user.email)
    ).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    
    hashed_password = auth.get_password_hash(user.password)
    
    keyserver_payload = {
        "user_email" : user.email
    }
    
    generate_key_pair = requests.post(url=f"{KEYSERVER}/generate-key-pair", params=keyserver_payload)
    
    response = generate_key_pair.json()
    
    public_key = response['encoded_public_key']
    
    print(public_key)
    
    db_user = models.User(
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        user_type=int(user.user_type),
        national_id=encrypt_with_public_key(public_key,user.national_id),
        dob=user.dob,
        hashed_password=hashed_password,
        public_key= public_key
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return {"message":"successfully registered"}

# Login route
@app.post("/login")
def login(loginInfo: schemas.UserLogin, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == loginInfo.email).first()
    if not user or not auth.verify_password(loginInfo.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    
    # Generate JWT token
    access_token = auth.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer", "userGroup" : user.user_type, "userName" : user.first_name + user.last_name}



@app.post("/user-info", response_model=schemas.UserInfoResponse)
def get_user_info(token_input: schemas.TokenInput, db: Session = Depends(get_db)):
    
    user = auth.get_current_user(token=token_input.token, db=db)
    
    json = {
        "data" : user.national_id,
        "token" : token_input.token
    }
    
    response = requests.post(url=f"{KEYSERVER}/decrypt-data", json=json).json()
    
    if(response['decrypted_data']):
        return schemas.UserInfoResponse(
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email,
            user_type=user.user_type,
            national_id=response['decrypted_data'],
            dob=user.dob,
            public_key=user.public_key
        )
    else:
        return {"message" : "User Authentiation Failed"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)