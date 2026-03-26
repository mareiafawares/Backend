from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import connection, models

router = APIRouter() 

@router.get("/all")
def get_all_shops(category: Optional[str] = None, db: Session = Depends(connection.get_db)):
    """
    Fetches all approved shops only.
    """
    query = db.query(models.Shop).filter(models.Shop.is_approved == True)
    
    if category:
        query = query.filter(
            (models.Shop.description.contains(category)) | 
            (models.Shop.name.contains(category))
        )
        
    shops = query.all()
    
    return [
        {
            "id": s.id,
            "name": s.name,
            "description": s.description,
            "image_url": s.image_url,
            "owner_id": s.owner_id,
            "is_approved": s.is_approved
        } for s in shops
    ]

@router.get("/{shop_id}")
def get_shop_details(shop_id: int, db: Session = Depends(connection.get_db)):
    """
    Fetches details of a specific shop.
    """
    shop = db.query(models.Shop).filter(models.Shop.id == shop_id).first()
    
    if not shop:
        raise HTTPException(status_code=404, detail="Shop not found")
        
    return {
        "id": shop.id,
        "name": shop.name,
        "description": shop.description,
        "image_url": shop.image_url,
        "owner_id": shop.owner_id,
        "is_approved": shop.is_approved,
        "products_count": len(shop.products) 
    }