from fastapi import APIRouter, HTTPException, Depends
from models.user import User
from db import users_collection
import json
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta
from passlib.context import CryptContext
from jose import JWTError, jwt
from models.user import User, UserInDB, AuthUser, RegisterUser
from services.auth import verify_password, get_user, create_access_token, pwd_context

load_dotenv()

router = APIRouter()

@router.post("/login")
async def login_for_access_token(user: AuthUser):
    user = await authenticate_user(user.email, user.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    access_token_expires = timedelta(minutes=int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES')))
    access_token = create_access_token(
        data={"sub": user['email']}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/register")
async def register_user(user: RegisterUser):
    
    try:
        hashed_password = pwd_context.hash(user.password)
        user = {"username": user.username, "email": user.email, "hashed_password": hashed_password,"assistant_id": '', "thread_id": ''}
        
        result = await users_collection.insert_one(user)
        inserted_id = str(result.inserted_id)
        return {"user_id": inserted_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating user: {str(e)}")

async def authenticate_user(email: str, password: str):
    user = await get_user(email)
    if not user:
        return False
    if not verify_password(password, user['hashed_password']):
        return False
    return user    