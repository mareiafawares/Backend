from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime


class OrderItemBase(BaseModel):
    product_id: int
    quantity: int
    price_at_purchase: float
   
    shop_id: int  
    product_name: Optional[str] = None
    product_image: Optional[str] = None

class OrderItemCreate(OrderItemBase):
    pass

class OrderItem(OrderItemBase):
    id: int
    model_config = ConfigDict(from_attributes=True)



class OrderCreate(BaseModel):
    full_name: str
    phone_number: str
    city: str
    address_details: str
    delivery_notes: Optional[str] = None
    
    
    total_price: float
    
    
    items: List[OrderItemCreate] 



class OrderResponse(BaseModel):
    id: int
    status: str
    total_price: float
    shop_id: int 
    created_at: datetime
    items: List[OrderItem] = []

    model_config = ConfigDict(from_attributes=True)



class OrderStatusUpdate(BaseModel):
    status: str