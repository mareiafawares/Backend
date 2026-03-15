from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form
from sqlalchemy.orm import Session
import os
import shutil
from typing import List
from database.connection import get_db 
from database import models
from schemas import product_schemas 

router = APIRouter(tags=["Products Management"])


@router.get("/shop/{shop_id}", response_model=List[product_schemas.Product])
async def get_shop_products(shop_id: int, db: Session = Depends(get_db)):
    products = db.query(models.Product).filter(models.Product.shop_id == shop_id).all()
    
    return products


@router.post("/add/{shop_id}", status_code=status.HTTP_201_CREATED, response_model=product_schemas.Product)
async def create_product(
    shop_id: int,
    name: str = Form(...),
    price: float = Form(...),
    description: str = Form("No description"),
    stockQuantity: int = Form(0),
    image: UploadFile = File(...),
    db: Session = Depends(get_db)
):
   
    db_shop = db.query(models.Shop).filter(models.Shop.id == shop_id).first()
    if not db_shop:
        raise HTTPException(status_code=404, detail="Shop not found")

    
    file_extension = image.filename.split(".")[-1]
    unique_filename = f"prod_{shop_id}_{os.urandom(4).hex()}.{file_extension}"
    
   
    file_path = f"static/products/{unique_filename}"

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)

    
    image_url = f"http://192.168.1.5:8000/{file_path}"

    
    new_product = models.Product(
        name=name,
        price=price,
        description=description,
        stockQuantity=stockQuantity,
        imageUrl=image_url,
        shop_id=shop_id,
        owner_id=db_shop.owner_id
    )
    
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product


@router.delete("/delete/{product_id}")
async def delete_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    

    db.delete(product)
    db.commit()
    return {"message": "Product deleted successfully"}