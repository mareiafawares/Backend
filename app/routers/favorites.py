from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import connection, models
from typing import List

router = APIRouter(prefix="/favorites", tags=["Favorites"])


@router.post("/toggle/{product_id}")
def toggle_favorite(product_id: int, user_id: int, db: Session = Depends(connection.get_db)):
   
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

   
    fav_entry = db.query(models.Favorite).filter(
        models.Favorite.user_id == user_id, 
        models.Favorite.product_id == product_id
    ).first()

    if fav_entry:
       
        db.delete(fav_entry)
        db.commit()
        return {"message": "Removed from favorites", "is_favorite": False}
    else:
      
        new_fav = models.Favorite(user_id=user_id, product_id=product_id)
        db.add(new_fav)
        db.commit()
        return {"message": "Added to favorites", "is_favorite": True}


@router.get("/all/{user_id}")
def get_favorites(user_id: int, db: Session = Depends(connection.get_db)):
    """Fetch all favorite products for a specific user"""
    favs = db.query(models.Favorite).filter(models.Favorite.user_id == user_id).all()
    
    result = []
    for f in favs:
        p = f.product  
        result.append({
            "id": p.id,
            "name": p.name,
            "description": p.description,
            "price": p.price,
            "image_url": p.images[0].url if p.images else "", 
            "shop_id": p.shop_id,
            "category": p.category,
            "status": p.status
        })
    return result