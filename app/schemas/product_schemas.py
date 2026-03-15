from pydantic import BaseModel, ConfigDict
from typing import Optional

class ProductBase(BaseModel):
    name: str
    price: float
    description: Optional[str] = "No description"
    imageUrl: str  
    stockQuantity: int

class ProductCreate(ProductBase):
    
    pass

class Product(ProductBase):
    id: int
    shop_id: int

    
    model_config = ConfigDict(from_attributes=True)