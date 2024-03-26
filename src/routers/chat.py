from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from pydantic import BaseModel
from services.assistant import AssistantManager
from db import users_collection, files_collection
from bson import ObjectId
from bson.binary import Binary
from datetime import datetime
from typing import Optional
from models.user import User, Token
from jose import JWTError, jwt
import os
import tempfile
from services.auth import get_current_user

router = APIRouter()

assistant_manager = AssistantManager()
    

async def save_file(file: UploadFile) -> str:
    contents = await file.read()
    file_data = Binary(contents)
    saved_file = await files_collection.insert_one({"file_data": file_data, "uploaded_at": datetime.now()})
    return str(saved_file.inserted_id)

@router.post("/upload")
async def upload_file(file: UploadFile = File(...), current_user: User = Depends(get_current_user)):
    try:
        # file_id = await save_file(file)
        temp_file_path = f"/tmp/{file.filename}"
        with open(temp_file_path, 'wb') as temp_file:
            temp_file.write(await file.read())

        with open(temp_file_path, 'rb') as temp_file:
            res = assistant_manager.upload_file(temp_file)

        # Perform necessary operations with the assistant ID
        await users_collection.update_one(
            {"username": current_user['username']},
            {"$push": {"documents": file.filename}, "$set": {"assistant_id": res["assistant_id"], "thread_id": res["thread_id"]}}
        )
        return res

    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=f"Error uploading file: {str(e)}")


@router.get("/get_answers")
async def get_answers(question: str, current_user: User = Depends(get_current_user)):
    try:
        answers = assistant_manager.get_answers(question, current_user['assistant_id'], current_user['thread_id'])
        return {"answers": answers}
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))  