from fastapi import APIRouter, HTTPException, Depends
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import JWTError, jwt
from db import users_collection
from models.user import User, UserInDB
from dotenv import load_dotenv
import os
from typing import Optional
from fastapi.security import  HTTPBearer

oauth2_scheme = HTTPBearer()

load_dotenv()

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


async def get_user(email: str):
    user_data = await users_collection.find_one({"email": email})
    if user_data:
        return user_data


def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, os.getenv('SECRET_KEY'), algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)) -> Optional[User]:
    try:
        token = token.dict()
        token = token['credentials']
        payload = jwt.decode(token, os.getenv('SECRET_KEY'), algorithms=['HS256'])
        user = await users_collection.find_one({"email": payload.get('sub')})
        if user:
            return user
        else:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")