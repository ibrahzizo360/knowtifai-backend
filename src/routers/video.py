from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from services.assistant import AssistantManager
from langchain_community.document_loaders import TextLoader
from db import users_collection
from bson.binary import Binary
from datetime import datetime
from models.user import User
from models.chat import QuestionRequest
from services.auth import get_current_user
from services.chat import load_docs, create_vector_store, create_video_upload_chain, generate_session_id, video_upload_queue
from langchain_core.messages import HumanMessage, AIMessage
from bson import json_util 
from langchain_community.vectorstores.mongodb_atlas import MongoDBAtlasVectorSearch
from langchain_openai import OpenAIEmbeddings
from fastapi.responses import StreamingResponse
from services.callbacks import RetrieverCallbackHandler
from langchain_text_splitters import CharacterTextSplitter
import os
import asyncio
from threading import Thread
from queue import Queue
from dotenv import load_dotenv
from db import sessions_collection
from services.document import upload_document_to_aws
from services.video import get_transcript, get_transcript, upload_transcript_to_aws
from models.video import VideoRequest
from langchain_chroma import Chroma
 
load_dotenv()

router = APIRouter()

@router.post('/v1/upload_video')
async def upload_video(request: VideoRequest, current_user: User = Depends(get_current_user)):
    session_id = generate_session_id()
    # transcript = await get_transcript(request.video_url)
    
    if not os.path.exists("../data/transcripts"):
        os.makedirs("../data/transcripts")
        print(f"Directory '{"transcripts"}' created.")
    
    transcript_file_path = f"../data/transcripts/{session_id}.txt"
    
    segments = request.transcript
    
    with open(transcript_file_path, 'w') as file:
        for segment in segments:
            start_time = segment['start']
            end_time = segment['end']
            text = segment['text']
            file.write(f"[{start_time:.2f} - {end_time:.2f}] {text}\n")
    
    loader = TextLoader(transcript_file_path)
    documents = loader.load()
    embeddings = OpenAIEmbeddings()
    
    # split it into chunks
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    docs = text_splitter.split_documents(documents)

    db = Chroma.from_documents(docs, embeddings, persist_directory="../data/chroma_db")
    
    chain = create_video_upload_chain(db)
    
    chat_history = []
        
    def generate():
        # chain.invoke({"question": question, "chat_history": []},{"callbacks":[chain_callback_handler]})
        response = chain.invoke({
        "question": """Greet the user and then proceed to give a brief overview of the video material. 
                It should not be more than 60 words. End by wishing the user the best in learning.""",
                
        "chat_history": chat_history})
        chat_history.append({"role": "bot", "text": response['answer']})
        
        sessions_collection.insert_one(
        {"session_id": session_id, "chat_history": chat_history,
        "type": "video", "name": request.title, "video_url": request.video_url,
        "transcript": segments, "user_id": current_user['_id']}
        )
           
    def start_generation():
        # Creating a thread with generate function as a target
        thread = Thread(target=generate)
        # Starting the thread
        thread.start()
            
        
    async def response_generator():
        start_generation()
        yield str({"session_id": session_id})

        # Starting an infinite loop
        while True:
        # Obtain the value from the streamer queue
                value = video_upload_queue.get()
                # Check for the stop signal, which is None in our case
                if value == None:
                        # If stop signal is found break the loop
                        break
                # Else yield the valuex
                yield str(value)
                # statement to signal the queue that task is done
                video_upload_queue.task_done()

                await asyncio.sleep(0.1)
                
    await users_collection.update_one(
        {"username": current_user['username']},
        {"$push": {"sessions": session_id}}
    )
    
    return StreamingResponse(response_generator(), media_type='text/event-stream')


@router.post('/transcript')
async def get_transcript_segments(request: VideoRequest):
    transcript = await get_transcript(request.video_url)
    print(transcript.segments)
    return {"transcript": transcript.segments}