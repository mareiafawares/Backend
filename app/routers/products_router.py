from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List


from database.connection import get_db 
from database import models
from schemas import product_schemas 

router = APIRouter(
    prefix="/products",
    tags=["Products Management"]
)

@router.get("/shop/{shop_id}", response_model=List[product_schemas.Product])
def get_products_by_shop(shop_id: int, db: Session = Depends(get_db)):
    products = db.query(models.Product).filter(models.Product.shop_id == shop_id).all()
    return products

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=product_schemas.Product)
def create_product(product: product_schemas.ProductCreate, db: Session = Depends(get_db)):
    new_product = models.Product(**product.dict())
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product