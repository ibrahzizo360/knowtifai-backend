from pydantic import BaseModel
from typing import Optional


class ChatRequest(BaseModel):
    question: str
    transcript_text: str

class ChatResponse(BaseModel):
    chat_completion: str   

class QuestionRequest(BaseModel):
    question: str
    session_id: Optional[str] = None

class SummaryRequest(BaseModel):
    transcript_text: str   