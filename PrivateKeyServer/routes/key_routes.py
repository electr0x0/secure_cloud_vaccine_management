from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import time

from core.database import get_db
from core.models import schemas
from services.key_management import store_user_key_pair, decrypt_data
from core.metrics import RAW_CRYPTO_TIME, ACTIVE_KEY_PAIRS

router = APIRouter()

@router.post("/generate-key-pair", response_model=schemas.KeyResponse)
async def generate_key_pair(user_email: str, db: Session = Depends(get_db)):
    """Generates and stores a new RSA/X25519 key pair for a user and returns the public key."""
    try:
        start_time = time.time()
        public_key = store_user_key_pair(db, user_email)
        RAW_CRYPTO_TIME.labels(operation_type="key_generation").observe(time.time() - start_time)
        ACTIVE_KEY_PAIRS.inc()
        return schemas.KeyResponse(encoded_public_key=public_key)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/decrypt-data", response_model=schemas.DataDecryptResponse)
async def decrypt_data_endpoint(request: schemas.KeyRequest, db: Session = Depends(get_db)):
    """Decrypts user data using the private key."""
    try:
        start_time = time.time()
        decrypted_data = decrypt_data(
            db, 
            user_email=request.user_email, 
            encrypted_data=request.data
        )
        RAW_CRYPTO_TIME.labels(operation_type="decryption").observe(time.time() - start_time)
        return schemas.DataDecryptResponse(decrypted_data=decrypted_data)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))