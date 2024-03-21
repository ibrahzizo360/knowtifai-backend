from pydantic import BaseModel

class User(BaseModel):
    email: str
    description: str = None