from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict
from app.database.connection import get_db
from app.database import models
from app.schemas import order_schemas 
from app.core.oauth2 import get_current_user 

router = APIRouter(tags=["Orders Management"])

@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_order(
    order_data: order_schemas.OrderCreate, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
   
    grouped_items: Dict[int, List[order_schemas.OrderItemCreate]] = {}
    
    for item in order_data.items:
        if item.shop_id not in grouped_items:
            grouped_items[item.shop_id] = []
        grouped_items[item.shop_id].append(item)

    created_orders_ids = []

    try:
       
        for shop_id, items in grouped_items.items():
           
            shop_order_total = sum(item.quantity * item.price_at_purchase for item in items)
            
            new_order = models.Order(
                full_name=order_data.full_name,
                phone_number=order_data.phone_number,
                city=order_data.city,
                address_details=order_data.address_details,
                delivery_notes=order_data.delivery_notes,
                total_price=shop_order_total,
                status="Pending",
                buyer_id=current_user.id, 
                shop_id=shop_id 
            )
            
            db.add(new_order)
            db.flush() 
            created_orders_ids.append(new_order.id)

            
            for item in items:
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

        db.commit()
        return {
            "message": f"Successfully created {len(created_orders_ids)} orders for different shops.",
            "order_ids": created_orders_ids
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/my-orders") 
def get_user_orders(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    
    orders = db.query(models.Order).filter(models.Order.buyer_id == current_user.id).all()
    
    results = []
    for o in orders:
        items_in_order = db.query(models.OrderItem).filter(models.OrderItem.order_id == o.id).all()
        
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
                "price_at_purchase": float(i.price_at_purchase),
                "product_name": getattr(i, 'product_name', "Product"),
                "product_image": getattr(i, 'product_image', "")
            })
        results.append({
            "id": o.id,
            "fullName": o.full_name,
            "phoneNumber": o.phone_number,
            "city": o.city,
            "totalPrice": float(o.total_price),
            "status": o.status,
            "createdAt": str(o.created_at),
            "items": item_list
        })
    return results


@router.put("/update-status/{order_id}")
def update_order_status(
    order_id: int, 
    status: str, 
    db: Session = Depends(get_db)
):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail=f"Order {order_id} not found")
    
    order.status = status
    db.commit()
    return {"message": f"Status updated to {status} successfully"}