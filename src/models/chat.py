from pydantic import BaseModel

class ChatRequest(BaseModel):
    question: str
    transcript_text: str

class ChatResponse(BaseModel):
    chat_completion: dict   