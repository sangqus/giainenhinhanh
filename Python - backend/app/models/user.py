from pydantic import BaseModel , Field
from datetime import datetime

class User(BaseModel):
    phone: str 
    username: str
    hashed_password: str 
    created_at: datetime = Field(default_factory = datetime.now) # tao usert moi lay thoi gian hien tai

class UserCreate(BaseModel):
    phone : str 
    username : str 
    password : str

class UserLogin(BaseModel):
    phone: str
    password: str 

class Token(BaseModel):
    access_token: str
    token_type: str 