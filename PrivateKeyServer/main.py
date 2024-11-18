# app/main.py
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from database import engine, get_db
import models
import schemas
import key_management
import base64
import uvicorn
import auth


models.Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Key Management API",
    description="API for managing RSA key pairs and decrypting data on-premises.",
    version="1.0.0"
)

@app.post("/generate-key-pair", response_model=schemas.KeyResponse)
def generate_key_pair(user_email: str, db: Session = Depends(get_db)):
    """Generates and stores a new RSA key pair for a user and returns the public key."""
    try:
        public_key = key_management.store_user_key_pair(db, user_email)
        return schemas.KeyResponse(encoded_public_key=public_key)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/decrypt-data", response_model=schemas.DataDecryptResponse)
def decrypt_data(request: schemas.KeyRequest, db: Session = Depends(get_db)):
    """Decrypts user data using the private key."""
    try:
        decrypted_data = key_management.decrypt_data(db, user_email=auth.get_user(request.token), encrypted_data=request.data)
        
        return schemas.DataDecryptResponse(decrypted_data=decrypted_data.encode().decode("utf-8"))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{e}")


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8001, reload=True)