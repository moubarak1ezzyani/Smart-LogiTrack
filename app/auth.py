import os
from dot-env import load-dotenv
from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

load-dotenv()
secret_key = os.getenv("secret_key_env")
algo = os.getenv("algo_env")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=30)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, secret_key, algorithm=algo)

def verify_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, secret_key, algorithms=[algo])
        return payload.get("sub")
    except:
        raise HTTPException(status_code=401, detail="Invalid token")