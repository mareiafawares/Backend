from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database.connection import get_db
from app.database import models
from app.schemas import order_schemas

router = APIRouter(tags=["Orders Management"])


@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_order(order_data: order_schemas.OrderCreate, db: Session = Depends(get_db)):
    
    total_price = 0
    for item in order_data.items:
        product = db.query(models.Product).filter(models.Product.id == item.product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail=f"Product {item.product_id} not found")
        total_price += product.price * item.quantity

    
    new_order = models.Order(
        user_id=order_data.user_id,
        shop_id=order_data.shop_id,
        total_price=total_price,
        status="Pending"
    )
    db.add(new_order)
    db.commit()
    db.refresh(new_order)

   
    for item in order_data.items:
        product = db.query(models.Product).filter(models.Product.id == item.product_id).first()
        order_item = models.OrderItem(
            order_id=new_order.id,
            product_id=item.product_id,
            quantity=item.quantity,
            price=product.price
        )
        db.add(order_item)
        
        
        product.stock_quantity -= item.quantity

    db.commit()
    return {"message": "Order created successfully", "order_id": new_order.id}


@router.get("/shop/{shop_id}")
async def get_shop_orders(shop_id: int, db: Session = Depends(get_db)):
    orders = db.query(models.Order).filter(models.Order.shop_id == shop_id).all()
    return orders


@router.put("/update-status/{order_id}")
async def update_order_status(order_id: int, status: str, db: Session = Depends(get_db)):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    order.status = status
    db.commit()
    return {"message": f"Order status updated to {status}"}