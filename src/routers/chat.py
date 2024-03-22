from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from pydantic import BaseModel
from services.assistant import AssistantManager
from db import users_collection
from bson import ObjectId
from bson.binary import Binary
from datetime import datetime
from typing import Optional
from models.user import User, Token
from jose import JWTError, jwt
import os
from services.auth import get_current_user

router = APIRouter()

assistant_manager = AssistantManager()
    

async def save_file(file: UploadFile) -> str:
    contents = await file.read()
    file_data = Binary(contents)
    saved_file = await users_collection.insert_one({"file_data": file_data, "uploaded_at": datetime.now()})
    return str(saved_file.inserted_id)

@router.post("/upload")
async def upload_file(file: UploadFile = File(...), current_user: User = Depends(get_current_user)):
    try:
        file_id = await save_file(file)
        await users_collection.update_one({"username": current_user['username']}, {"$push": {"documents": file_id}})
        await assistant_manager.upload_file(file)
        return {"file_id": file_id, "message": "File uploaded successfully"}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=f"Error uploading file: {str(e)}")
