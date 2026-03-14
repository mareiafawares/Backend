from pydantic import BaseModel, EmailStr
from enum import Enum
from typing import Optional, List


class UserRegisterRole(str, Enum):
    admin = "admin"
    seller = "seller"
    customer = "customer"


class ProductBase(BaseModel):
    name: str
    price: float
    description: Optional[str] = None
    imageUrl: str
    stockQuantity: int
    shop_id: int

class ProductCreate(ProductBase):
    pass

class Product(ProductBase):
    id: int

    class Config:
        from_attributes = True


class ShopOut(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    is_approved: bool
    has_shop_request: bool
    owner_id: int
    

    class Config:
        from_attributes = True


class UserBase(BaseModel):
    username: str
    email: EmailStr


class UserCreate(UserBase):
    password: str
    role: UserRegisterRole


class UserLoginSchema(BaseModel):
    email: EmailStr
    password: str


class ShopCreateRequest(BaseModel):
    shop_name: str
    shop_description: str


class UserOut(BaseModel):
    id: int
    username: str
    email: EmailStr
    role: str
    shops: List[ShopOut] = [] 

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None