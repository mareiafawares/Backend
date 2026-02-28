from pydantic import BaseModel , EmailStr
from typing import Optional
class UserBase(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserCreate(UserBase):
    id: int
    username: str
    email: EmailStr

    class Config:
        from_attributes = True

class UserOut(BaseModel):
    id: int
    
class Config:
    from_attributes = True