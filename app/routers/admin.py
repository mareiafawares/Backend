from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import connection, models
from schemas import user_schemas

router = APIRouter(tags=["Admin Management"])


@router.get("/users", response_model=List[user_schemas.UserOut])
def get_all_users(db: Session = Depends(connection.get_db)):
    return db.query(models.User).all()


@router.get("/shop-requests")
def get_pending_shops(db: Session = Depends(connection.get_db)):
    
    requests = db.query(models.Shop).filter(models.Shop.is_approved == False).all()
    return requests


@router.put("/approve-shop/{shop_id}")
def approve_shop(shop_id: int, approve: bool, db: Session = Depends(connection.get_db)):
    shop = db.query(models.Shop).filter(models.Shop.id == shop_id).first()
    if not shop:
        raise HTTPException(status_code=404, detail="Shop not found")
    
    if approve:
        shop.is_approved = True
    else:
        db.delete(shop) 
    
    db.commit()
    return {"message": "Status updated", "approved": approve}