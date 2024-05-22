from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from services.assistant import AssistantManager
from db import users_collection
from bson.binary import Binary
from datetime import datetime
from models.user import User
from models.chat import QuestionRequest
from services.auth import get_current_user
from services.chat import load_docs, create_vector_store, create_chat_chain, create_default_chain,create_upload_chain, generate_session_id, upload_streamer_queue,chat_streamer_queue, streaming_callback_handler_upload,chain_callback_handler
from langchain_core.messages import HumanMessage, AIMessage
from bson import json_util 
from langchain_community.vectorstores.mongodb_atlas import MongoDBAtlasVectorSearch
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv
from fastapi.responses import StreamingResponse
from services.callbacks import RetrieverCallbackHandler
import os
import asyncio
from threading import Thread
from queue import Queue
from dotenv import load_dotenv
from db import sessions_collection
from services.document import upload_document_to_aws
from services.video import get_audio_path, get_transcript
from models.video import VideoRequest


load_dotenv()

router = APIRouter()

@router.post('/v1/upload_video')
async def upload_video(request: VideoRequest):
    session_id = generate_session_id()
    audio_path = get_audio_path()
    transcript = get_transcript(audio_path)
    
    
    pass