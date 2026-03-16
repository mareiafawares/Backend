import os
import shutil
from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form
from sqlalchemy.orm import Session
from database.connection import get_db 
from database import models


router = APIRouter()


@router.get("/all")
async def get_all_products(db: Session = Depends(get_db)):
    products = db.query(models.Product).all()
    
    results = []
    for p in products:
        results.append({
            "id": p.id,
            "name": p.name,
            "description": p.description,
            "price": p.price,
            "stock_quantity": p.stockQuantity,
            "status": p.status,
            "shop_id": p.shop_id,
            "category": p.category,
            
            "images": [{"id": img.id, "url": img.url} for img in p.images],
            "reviews": [{"id": r.id, "rating": r.rating, "comment": r.comment} for r in p.reviews]
        })
    return results


@router.get("/shop/{shop_id}")
async def get_shop_products(shop_id: int, db: Session = Depends(get_db)):
    products = db.query(models.Product).filter(models.Product.shop_id == shop_id).all()
    
    results = []
    for p in products:
        results.append({
            "id": p.id,
            "name": p.name,
            "description": p.description,
            "price": p.price,
            "stock_quantity": p.stockQuantity,
            "shop_id": p.shop_id,
            "images": [{"id": img.id, "url": img.url} for img in p.images],
            "reviews": []
        })
    return results


@router.post("/add/{shop_id}", status_code=status.HTTP_201_CREATED)
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

    try:
      
        new_product = models.Product(
            name=name,
            price=price,
            description=description,
            stockQuantity=stockQuantity,
            shop_id=shop_id,
            owner_id=db_shop.owner_id,
            status="Available",
            is_new=True,
            is_approved=False
        )
        
        db.add(new_product)
        db.flush() 

        
        upload_dir = "static/products"
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir, exist_ok=True)
            
        file_extension = image.filename.split(".")[-1]
        unique_filename = f"prod_{new_product.id}_{os.urandom(2).hex()}.{file_extension}"
        file_path = os.path.join(upload_dir, unique_filename).replace("\\", "/")

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)

        
        image_url = f"http://192.168.1.5:8000/{file_path}"
        new_product_image = models.ProductImage(
            url=image_url,
            product_id=new_product.id
        )
        
        db.add(new_product_image)
        db.commit() 
        db.refresh(new_product)
        
        return {"message": "Product and Image created successfully", "product_id": new_product.id}

    except Exception as e:
        db.rollback()
        print(f"DATABASE ERROR: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create product: {str(e)}")


@router.delete("/delete/{product_id}")
async def delete_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
   
    for img in product.images:
        try:
           
            local_path = img.url.split("8000/")[-1]
            if os.path.exists(local_path):
                os.remove(local_path)
        except:
            pass

    db.delete(product)
    db.commit()
    return {"message": "Product and its images deleted successfully"}