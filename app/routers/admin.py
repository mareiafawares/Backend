from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import connection, models
from app.schemas import user_schemas
from app.core.oauth2 import require_admin

router = APIRouter(tags=["Admin Management"])


@router.get("/users", response_model=List[user_schemas.UserOut])
def get_all_users(
    db: Session = Depends(connection.get_db),
    _admin=Depends(require_admin),
):
    return db.query(models.User).all()


@router.get("/shop-requests")
def get_pending_shops(
    db: Session = Depends(connection.get_db),
    _admin=Depends(require_admin),
):
    requests = db.query(models.Shop).filter(models.Shop.is_approved == False).all()
    return requests


@router.put("/approve-shop/{shop_id}")
def approve_shop(
    shop_id: int,
    approve: bool,
    db: Session = Depends(connection.get_db),
    _admin=Depends(require_admin),
):
    shop = db.query(models.Shop).filter(models.Shop.id == shop_id).first()
    if not shop:
        raise HTTPException(status_code=404, detail="Shop not found")
    
    if approve:
        shop.is_approved = True
    else:
        db.delete(shop) 
    
    db.commit()
    return {"message": "Status updated", "approved": approve}