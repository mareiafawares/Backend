from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime


class OrderItemBase(BaseModel):
    product_id: int
    quantity: int

class OrderItemCreate(OrderItemBase):
    pass

class OrderItem(OrderItemBase):
    id: int
    price: float
    model_config = ConfigDict(from_attributes=True)


class OrderBase(BaseModel):
    shop_id: int
    user_id: int

class OrderCreate(OrderBase):
    items: List[OrderItemCreate] 

class Order(OrderBase):
    id: int
    total_price: float
    status: str
    created_at: datetime
    items: List[OrderItem]
    
    model_config = ConfigDict(from_attributes=True)