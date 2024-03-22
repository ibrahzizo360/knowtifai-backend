from pydantic import BaseModel

class User(BaseModel):
    _id: str
    email: str
    username: str
    documents: list[str]
    hashed_password: str

class AuthUser(BaseModel):
    email: str
    password: str

class RegisterUser(BaseModel):
    email: str
    username: str
    password: str    


class UserInDB(User):
    hashed_password: str    

class Token(BaseModel):
    access_token: str
    token_type: str
