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
import tempfile
from models.chat import QuestionRequest
from services.auth import get_current_user
from services.chat import load_docs, create_vector_store, create_chain, generate_session_id
from langchain_core.messages import HumanMessage, AIMessage
from bson import json_util 
from langchain_community.vectorstores import MongoDBAtlasVectorSearch
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv
import os

load_dotenv()


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


@router.post("/get_answers")
async def get_answers(request: QuestionRequest , current_user: User = Depends(get_current_user)):
    try:
        answer = assistant_manager.get_answers(request.question, current_user['assistant_id'], current_user['thread_id'])
        return {"answer": answer}
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    
    
    
    
@router.post("/v1/upload")
async def upload_file(file: UploadFile = File(...), current_user: User = Depends(get_current_user)):
    # try:
        # file_id = await save_file(file)
        temp_file_path = f"/tmp/{file.filename}"
        with open(temp_file_path, 'wb') as temp_file:
            temp_file.write(await file.read())

        
        docs = load_docs(temp_file_path)
        vectorStore = create_vector_store(docs)
        chain = create_chain(vectorStore)
        
        chat_history = []
        
        res = chain.invoke({
            "input": """Greet the user and then proceed to give a brief overview of the uploaded learning material or document. 
                        It should not be more than 60 words. End by wishing the user the best in learning.""",
                        
            "chat_history": chat_history,
        })
        
        assistant_res = AIMessage(content=res['answer'], role='system')
        
        assistant_res_json = json_util.loads(assistant_res.json())
        assistant_res_json['role'] = 'system' 
        
        session_id = generate_session_id()

        # Perform necessary operations with the assistant ID
        await users_collection.update_one(
            {"username": current_user['username']},
            {"$push": {"documents": file.filename}, "$push": {"chat_history": assistant_res_json}, "$set": {"session_id": session_id}}
        )
        return res['answer']

    # except Exception as e:
    #     print(e)
    #     raise HTTPException(status_code=500, detail=f"Error uploading file: {str(e)}")    
    
    
    
@router.post("/v1/get_answers")
async def get_answers(request: QuestionRequest , current_user: User = Depends(get_current_user)):
    
    
    db = MongoDBAtlasVectorSearch.from_connection_string(
    os.getenv('MONGO_URL'),
    'embeddings.embeddings',
    OpenAIEmbeddings(disallowed_special=()),
    index_name='vector_index',
    )
    
    chain = create_chain(db)
    
    chat_history = current_user['chat_history']
    
    
    print('chat_history', chat_history)
    
    res = chain.invoke({
        "input": request.question,
        "chat_history": chat_history,
    })
    
    assistant_res = AIMessage(content=res['answer'])
    user_res = HumanMessage(content=request.question)
    
    assistant_res_json = json_util.loads(assistant_res.json())
    assistant_res_json['role'] = 'system' 
    
    user_res_json = json_util.loads(user_res.json())
    user_res_json['role'] = 'user'
    
    # Perform necessary operations with the assistant ID
    await users_collection.update_one(
        {"username": current_user['username']},
        {"$push": {"chat_history": {"$each": [user_res_json, assistant_res_json]}}}
    )
    
    return res['answer']