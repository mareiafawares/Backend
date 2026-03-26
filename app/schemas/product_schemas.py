from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime

class ProductImageOut(BaseModel):
    id: int
    url: str

    model_config = ConfigDict(from_attributes=True)


class ProductBase(BaseModel):
    name: str
    price: float
    description: Optional[str] = "No description"
    imageUrl: str
    stockQuantity: int


class ProductCreate(ProductBase):
    pass


class ProductAddRequest(BaseModel):
    """JSON body for POST /products/add/{shop_id}"""
    name: str
    price: float
    description: Optional[str] = None
    stock_quantity: int = 0
    image_urls: Optional[List[str]] = None 


class Product(ProductBase):
    id: int
    shop_id: int

    model_config = ConfigDict(from_attributes=True)


class ReviewCreate(BaseModel):
    """Data required from the Flutter app when adding a new review"""
    product_id: int
    rating: int  
    comment: str


class ReviewOut(BaseModel):
    """The review format displayed to the customer on the product details page"""
    id: int
    user_id: int
    rating: int
    comment: str
    created_at: datetime 

    model_config = ConfigDict(from_attributes=True)


class ProductOut(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    price: float
    discount_price: Optional[float] = None
    stock_quantity: int
    status: str
    shop_id: int
    category: Optional[str] = None
    is_new: bool
    is_approved: bool
    images: List[ProductImageOut] = []
    reviews: List[ReviewOut] = []

    model_config = ConfigDict(from_attributes=True)


class ProductImagesAddRequest(BaseModel):
    urls: List[str]


class ProductUpdateRequest(BaseModel):
    """JSON body for PATCH /products/{product_id}. Only send fields to update."""
    name: Optional[str] = None
    price: Optional[float] = None
    description: Optional[str] = None
    stock_quantity: Optional[int] = None
    discount_price: Optional[float] = None
    category: Optional[str] = None
    status: Optional[str] = None
    is_new: Optional[bool] = None