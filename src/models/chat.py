from pydantic import BaseModel

class ChatRequest(BaseModel):
    question: str
    transcript_text: str

class ChatResponse(BaseModel):
    chat_completion: str   

class QuestionRequest(BaseModel):
    question: str
    session_id: str

class SummaryRequest(BaseModel):
    transcript_text: str   