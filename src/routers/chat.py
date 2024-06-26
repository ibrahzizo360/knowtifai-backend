from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from services.assistant import AssistantManager
from db import users_collection
from bson.binary import Binary
from datetime import datetime
from models.user import User
from models.chat import QuestionRequest
from services.auth import get_current_user
from services.chat import load_docs, create_vector_store, create_chat_chain, create_default_chain,create_upload_chain, generate_session_id
from langchain_core.messages import HumanMessage, AIMessage
from bson import json_util 
from langchain_community.vectorstores.mongodb_atlas import MongoDBAtlasVectorSearch
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv
from fastapi.responses import StreamingResponse
from services.callbacks import upload_streamer_queue,chat_streamer_queue,chain_callback_handler
import asyncio
import os
import asyncio
from threading import Thread
from queue import Queue
from dotenv import load_dotenv
from db import sessions_collection


load_dotenv()


router = APIRouter()
assistant_manager = AssistantManager()

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
async def upload_file(file: UploadFile = File(...)):
    # try:
        # file_id = await save_file(file)
        temp_file_path = f"/tmp/{file.filename}"
        with open(temp_file_path, 'wb') as temp_file:
            temp_file.write(await file.read())

        
        docs = load_docs(temp_file_path)
        vectorStore = create_vector_store(docs)
        chain = create_upload_chain(vectorStore)
        
        chat_history = []
        
        # res = chain.invoke({
        #     "question": """Greet the user and then proceed to give a brief overview of the uploaded learning material or document. 
        #                 It should not be more than 60 words. End by wishing the user the best in learning.""",
                        
        #     "chat_history": chat_history,
        # })
        
        def generate():
        # chain.invoke({"question": question, "chat_history": []},{"callbacks":[chain_handler]})
            chain.invoke({
            "question": """Greet the user and then proceed to give a brief overview of the uploaded learning material or document. 
                        It should not be more than 60 words. End by wishing the user the best in learning.""",
                        
            "chat_history": chat_history,
        })
            
            
        def start_generation():
            # Creating a thread with generate function as a target
            thread = Thread(target=generate)
            # Starting the thread
            thread.start()
        
        # assistant_res = AIMessage(content=res['answer'], role='system')
        
        # assistant_res_json = json_util.loads(assistant_res.json())
        # assistant_res_json['role'] = 'system' 
        
        # session_id = generate_session_id()

        # # Perform necessary operations with the assistant ID
        # await users_collection.update_one(
        #     {"username": current_user['username']},
        #     {"$push": {"documents": file.filename}, "$push": {"chat_history": assistant_res_json}, "$set": {"session_id": session_id}}
        # )
        
        async def response_generator():
            start_generation()

            # Starting an infinite loop
            while True:
                # Obtain the value from the streamer queue
                value = upload_streamer_queue.get()
                # Check for the stop signal, which is None in our case
                if value == None:
                    # If stop signal is found break the loop
                    break
                # Else yield the value
                yield value
                # statement to signal the queue that task is done
                upload_streamer_queue.task_done()

                await asyncio.sleep(0.1)
    
    
        return StreamingResponse(response_generator(), media_type='text/event-stream')
        
        
        
        # return res['answer']

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
    
    chain = create_default_chain(db)
    
    chat_history = current_user['chat_history']
    chat_history = []
    
    res = chain.invoke({
        "question": request.question,
        "chat_history": chat_history,
    })
    
    assistant_res = AIMessage(content=res['answer'])
    user_res = HumanMessage(content=request.question)
    
    assistant_res_json = json_util.loads(assistant_res.json())
    assistant_res_json['role'] = 'system' 
    
    user_res_json = json_util.loads(user_res.json())
    user_res_json['role'] = 'user'
    

    await users_collection.update_one(
        {"username": current_user['username']},
        {"$push": {"chat_history": {"$each": [user_res_json, assistant_res_json]}}}
    )
    
    doc = res['source_documents'][0].to_json()['kwargs']
    source_text = doc['page_content']
    page = doc['metadata']['page']
    
    print(page, source_text)
    
    return {
        "answer": res['answer'],
        "page": page,
        "source_text": source_text
    }


@router.get("/get_session/{session_id}")
async def get_session_info(session_id, current_user: User = Depends(get_current_user)):
    user = await users_collection.find_one({"username": current_user['username']})
    user_sessions = user['sessions']
    if session_id in user_sessions:
        session = await sessions_collection.find_one({"session_id": session_id}, {'_id': 0, 'user_id': 0})
        return session
    else:
        raise HTTPException(status_code=400, detail="Session not found")


@router.get("/get_user_sessions")
async def get_session_info(current_user: User = Depends(get_current_user)):
    user = await users_collection.find_one({"username": current_user['username']})
    
    if not user or 'sessions' not in user:
        return {"error": "User or sessions not found"}

    user_session_ids = user['sessions']
    
    # Assuming session IDs are stored as ObjectIds
    sessions = await sessions_collection.find({"session_id": {"$in": user_session_ids}}, {'_id': 0,'user_id': 0}).to_list(length=None)

    return sessions
    
    
    # else:
    #     raise HTTPException(status_code=400, detail="Session not found")
     