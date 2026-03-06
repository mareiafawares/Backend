from pydantic import BaseModel , EmailStr
from enum import Enum
from typing import Optional

class UserRegisterRole(str, Enum):
    
    seller = "seller"
    customer = "customer"

class UserBase(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserCreate(UserBase):
    username: str
    email: EmailStr    
    password: str
    role: UserRegisterRole

   

class UserOut(BaseModel):
    id: int
    username: str
    email: EmailStr
    role: str

class Config:
    from_attributes = True