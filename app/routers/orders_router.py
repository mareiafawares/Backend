from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database.connection import get_db
from app.database import models
from app.schemas import order_schemas 

router = APIRouter(tags=["Orders Management"])


@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_order(
    order_data: order_schemas.OrderCreate, 
    db: Session = Depends(get_db)
):
    new_order = models.Order(
        full_name=order_data.full_name,
        phone_number=order_data.phone_number,
        city=order_data.city,
        address_details=order_data.address_details,
        delivery_notes=order_data.delivery_notes,
        total_price=order_data.total_price,
        status="Pending",
        buyer_id=1, 
        shop_id=order_data.shop_id 
    )
    
    db.add(new_order)
    db.flush() 

    for item in order_data.items:
        product = db.query(models.Product).filter(models.Product.id == item.product_id).first()
        
        if not product:
            db.rollback()
            raise HTTPException(status_code=404, detail=f"Product {item.product_id} not found")
        
       
        first_image_url = ""
        if product.images and len(product.images) > 0:
            first_image_url = product.images[0].url

        order_item = models.OrderItem(
            order_id=new_order.id,
            product_id=item.product_id,
            quantity=item.quantity,
            price_at_purchase=item.price_at_purchase,
            product_name=product.name,
            product_image=first_image_url
        )
        db.add(order_item)
        
        
        product.stock_quantity -= item.quantity

    try:
        db.commit()
        db.refresh(new_order)
        return {"message": "Order placed successfully", "order_id": new_order.id}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/my-orders") 
def get_user_orders(db: Session = Depends(get_db)):
    
    user_id = 1 
    orders = db.query(models.Order).filter(models.Order.buyer_id == user_id).all()
    
    results = []
    for o in orders:
       
        items_in_order = db.query(models.OrderItem).filter(models.OrderItem.order_id == o.id).all()
        
       
        print(f"Order {o.id} has {len(items_in_order)} items") 

        item_list = []
        for i in items_in_order:
            item_list.append({
                "product_id": i.product_id,
                "quantity": i.quantity,
                "price_at_purchase": float(i.price_at_purchase),
                "product_name": getattr(i, 'product_name', "Product"),
                "product_image": getattr(i, 'product_image', "")
            })

        results.append({
            "id": o.id,
            "totalPrice": float(o.total_price),
            "status": o.status,
            "createdAt": str(o.created_at),
            "fullName": o.full_name or "Customer",
            "phoneNumber": o.phone_number or "",
            "city": o.city or "",
            "addressDetails": o.address_details or "",
            "items": item_list 
        })
    return results


@router.get("/shop/{shop_id}")
def get_shop_orders(shop_id: int, db: Session = Depends(get_db)):
    orders = db.query(models.Order).filter(models.Order.shop_id == shop_id).all()
    results = []
    for o in orders:
        items_in_order = db.query(models.OrderItem).filter(models.OrderItem.order_id == o.id).all()
        item_list = []
        for i in items_in_order:
            item_list.append({
                "product_id": i.product_id,
                "quantity": i.quantity,
                "price_at_purchase": i.price_at_purchase,
                "product_name": getattr(i, 'product_name', "Product"),
                "product_image": getattr(i, 'product_image', "")
            })
        results.append({
            "id": o.id,
            "fullName": o.full_name,
            "phoneNumber": o.phone_number,
            "city": o.city,
            "totalPrice": o.total_price,
            "status": o.status,
            "createdAt": str(o.created_at),
            "items": item_list
        })
    return results


@router.put("/update-status/{order_id}")
def update_order_status(order_id: int, status_update: order_schemas.OrderStatusUpdate, db: Session = Depends(get_db)):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail=f"Order {order_id} not found")
    
    order.status = status_update.status
    db.commit()
    return {"message": "Status updated successfully"}