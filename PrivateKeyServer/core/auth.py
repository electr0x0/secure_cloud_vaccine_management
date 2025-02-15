from jose import jwt
from config import SECRET_KEY, ALGORITHM

def get_user(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        
        return email
    except:
        return False