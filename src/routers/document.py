from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from services.assistant import AssistantManager
from db import users_collection
from bson.binary import Binary
from datetime import datetime
from models.user import User
from models.chat import QuestionRequest
from services.auth import get_current_user
from services.chat import load_docs, create_vector_store, create_chat_chain,create_upload_chain, generate_session_id
from langchain_core.messages import HumanMessage, AIMessage
from bson import json_util 
from langchain_community.vectorstores.mongodb_atlas import MongoDBAtlasVectorSearch
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv
from fastapi.responses import StreamingResponse
from services.callbacks import  upload_streamer_queue,chat_streamer_queue
import os
import asyncio
from threading import Thread
from queue import Queue
from dotenv import load_dotenv
from db import ATLAS_VECTOR_SEARCH_INDEX_NAME,COLLECTION_NAME,DB_NAME, sessions_collection
from services.document import upload_document_to_aws


load_dotenv()

router = APIRouter()


@router.post("/v2/upload")
async def upload_file(file: UploadFile = File(...), current_user: User = Depends(get_current_user)):
    try:

        temp_file_path = f"/tmp/{file.filename}"
        with open(temp_file_path, 'wb') as temp_file:
            temp_file.write(await file.read())

        
        file_url = await upload_document_to_aws(temp_file_path)
        
        docs = load_docs(temp_file_path)
        vectorStore = create_vector_store(docs)
        chain = create_upload_chain(vectorStore)
        
        chat_history = []
        
        def generate():
        # chain.invoke({"question": question, "chat_history": []},{"callbacks":[chain_callback_handler]})
            response = chain.invoke({
            "question": """Greet the user and then proceed to give a brief overview of the uploaded learning material or document. 
                        It should not be more than 60 words. End by wishing the user the best in learning.""",
                        
            "chat_history": chat_history})
            chat_history.append({"role": "bot", "text": response['answer']})
            
            sessions_collection.insert_one(
                {"session_id": session_id, "chat_history": chat_history,
                "type": "document", "name": file.filename,
                "file_url": file_url, "user_id": current_user['_id']}
                )
            
        session_id = generate_session_id()
           
        def start_generation():
            # Creating a thread with generate function as a target
            thread = Thread(target=generate)
            # Starting the thread
            thread.start()
        
        async def response_generator():
            start_generation()
            yield str({"session_id": session_id})
            yield str({"file_url": file_url})

            # Starting an infinite loop
            while True:
                # Obtain the value from the streamer queue
                value = upload_streamer_queue.get()
                # Check for the stop signal, which is None in our case
                if value == None:
                    # If stop signal is found break the loop
                    break
                # Else yield the valuex
                yield str(value)
                # statement to signal the queue that task is done
                upload_streamer_queue.task_done()

                await asyncio.sleep(0.1)
            
        await users_collection.update_one(
            {"username": current_user['username']},
            {"$push": {"sessions": session_id}}
        )
    
        return StreamingResponse(response_generator(), media_type='text/event-stream')
        

    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=f"Error uploading file: {str(e)}")  
    
    
    
@router.post("/v2/get_answers")
async def get_answers(request: QuestionRequest):
    
    db = MongoDBAtlasVectorSearch.from_connection_string(
    os.getenv('MONGO_URL'),
    DB_NAME + '.' + COLLECTION_NAME,
    OpenAIEmbeddings(disallowed_special=()),
    index_name='vector_index',
    )
    
    session = await sessions_collection.find_one({"session_id": request.session_id})
    
    chain = create_chat_chain(db)
    chat_history = session['chat_history']
    
    def generate(question):
        response = chain.invoke({"question": question, "chat_history": []})
        # chain.invoke({"question": question, "chat_history": []},{"callbacks":[chain_callback_handler]})
        
        chat_history.append({"role": "user", "text": question})
        chat_history.append({"role": "bot", "text": response['answer']})
        
        sessions_collection.update_one({"session_id": request.session_id},{"$set": {"chat_history": chat_history}})

    def start_generation(question):
        # Creating a thread with generate function as a target
        thread = Thread(target=generate, kwargs={"question": question})
        # Starting the thread
        thread.start()
        
    async def response_generator(query):
        start_generation(query)

        # Starting an infinite loop
        while True:
            # Obtain the value from the streamer queue
            value = chat_streamer_queue.get()
            # Check for the stop signal, which is None in our case
            if value == None:
                # If stop signal is found break the loop
                break
            # Else yield the value
            yield str(value)
            # statement to signal the queue that task is done
            chat_streamer_queue.task_done()

            await asyncio.sleep(0.1)
    
    return StreamingResponse(response_generator(request.question), media_type='text/event-stream')