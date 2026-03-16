from pydantic import BaseModel, EmailStr
from enum import Enum
from typing import Optional, List
from datetime import datetime


class UserRole(str, Enum):
    admin = "admin"
    seller = "seller"
    customer = "customer"


class ProductImageOut(BaseModel):
    id: int
    url: str

    class Config:
        from_attributes = True


class ReviewOut(BaseModel):
    id: int
    comment: Optional[str] = None
    rating: int
    created_at: datetime
    user_id: int
   

    class Config:
        from_attributes = True


class ProductBase(BaseModel):
    name: str
    price: float
    description: Optional[str] = None
    stockQuantity: int
    shop_id: int
    discountPrice: Optional[float] = None
    category: Optional[str] = None

class ProductCreate(ProductBase):
    pass


class ProductOut(ProductBase):
    id: int
    status: str
    is_new: bool
    is_approved: bool
    
    images: List[ProductImageOut] = []
    reviews: List[ReviewOut] = []
   
    sales_count: int = 0 

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
    role: UserRole

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class ShopCreateRequest(BaseModel):
    shopName: str
    shopDescription: str

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
    user: UserOut

class TokenData(BaseModel):
    email: Optional[str] = None