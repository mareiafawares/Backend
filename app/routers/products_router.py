import os
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.database import models
from app.schemas import product_schemas

router = APIRouter()


def _product_images(images: List) -> List[dict]:
    return [{"id": img.id, "url": img.url} for img in images]


def _product_to_dict(p: models.Product, include_reviews: bool = False) -> dict:
    out = {
        "id": p.id,
        "name": p.name,
        "description": p.description,
        "price": p.price,
        "discount_price": getattr(p, "discount_price", None),
        "stock_quantity": p.stock_quantity,
        "status": p.status,
        "shop_id": p.shop_id,
        "category": p.category,
        "is_new": p.is_new,
        "is_approved": p.is_approved,
        "images": _product_images(p.images),
    }
    if include_reviews:
        out["reviews"] = [
            {
                "id": r.id, 
                "rating": r.rating, 
                "comment": r.comment,
                "user_id": r.user_id,
                "created_at": r.created_at.isoformat() if r.created_at else None
            } for r in p.reviews
        ]
    return out


def _is_local_image_url(url: str) -> bool:
    return url.startswith("/static/") or "8000/" in url


def _local_path_from_url(url: str) -> Optional[str]:
    if url.startswith("/static/"):
        return url.lstrip("/")
    if "8000/" in url:
        return url.split("8000/")[-1]
    return None


@router.get("/all")
async def get_all_products(db: Session = Depends(get_db)):
    products = db.query(models.Product).all()
    return [_product_to_dict(p, include_reviews=True) for p in products]


@router.get("/shop/{shop_id}")
async def get_shop_products(shop_id: int, db: Session = Depends(get_db)):
    """List products for a shop (seller). Each item has full detail shape so cards can open details without an extra request."""
    products = db.query(models.Product).filter(models.Product.shop_id == shop_id).all()
    return [_product_to_dict(p, include_reviews=True) for p in products]


@router.get("/{product_id}")
async def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return _product_to_dict(product, include_reviews=True)


@router.patch("/{product_id}")
async def update_product(
    product_id: int,
    body: product_schemas.ProductUpdateRequest,
    db: Session = Depends(get_db),
):
    """Edit a product. Send only the fields you want to change (JSON body)."""
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    data = body.model_dump(exclude_unset=True)
    if not data:
        raise HTTPException(status_code=400, detail="No fields to update")
    for key, value in data.items():
        setattr(product, key, value)
    db.commit()
    db.refresh(product)
    return {"message": "Product updated", "product": _product_to_dict(product, include_reviews=True)}


@router.post("/add/{shop_id}", status_code=status.HTTP_201_CREATED)
async def create_product(
    shop_id: int,
    body: product_schemas.ProductAddRequest,
    db: Session = Depends(get_db),
):
    """
    Add a product with JSON: name, price, description (optional), stock_quantity, image_urls (optional list from /upload/image).
    """
    db_shop = db.query(models.Shop).filter(models.Shop.id == shop_id).first()
    if not db_shop:
        raise HTTPException(status_code=404, detail="Shop not found")

    try:
        new_product = models.Product(
            name=body.name,
            price=body.price,
            description=body.description or "No description",
            stock_quantity=body.stock_quantity,
            shop_id=shop_id,
            owner_id=db_shop.owner_id,
            status="Available",
            is_new=True,
            is_approved=False,
        )
        db.add(new_product)
        db.flush()

        for url in body.image_urls or []:
            db.add(models.ProductImage(url=url.strip(), product_id=new_product.id))

        db.commit()
        db.refresh(new_product)
        return {"message": "Product created successfully", "product_id": new_product.id, "product": _product_to_dict(new_product)}
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create product")


@router.post("/{product_id}/images", status_code=status.HTTP_201_CREATED)
async def add_product_images(
    product_id: int,
    body: product_schemas.ProductImagesAddRequest,
    db: Session = Depends(get_db),
):
    """Add image URLs to a product. Body: {"urls": ["/static/uploads/images/...", ...]}."""
    urls = body.urls
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    for url in urls:
        if isinstance(url, str) and url.strip():
            db.add(models.ProductImage(url=url.strip(), product_id=product_id))
    db.commit()
    db.refresh(product)
    return {"message": "Images added", "images": _product_images(product.images)}


@router.delete("/{product_id}/images/{image_id}")
async def delete_product_image(
    product_id: int,
    image_id: int,
    db: Session = Depends(get_db),
):
    """Remove one image from a product. Local files under /static/ are deleted from disk."""
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    img = next((i for i in product.images if i.id == image_id), None)
    if not img:
        raise HTTPException(status_code=404, detail="Image not found")
    url = img.url
    db.delete(img)
    db.commit()
    if _is_local_image_url(url):
        path = _local_path_from_url(url)
        if path and os.path.exists(path):
            try:
                os.remove(path)
            except Exception:
                pass
    return {"message": "Image deleted"}


@router.delete("/delete/{product_id}")
async def delete_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    for img in product.images:
        if _is_local_image_url(img.url):
            path = _local_path_from_url(img.url)
            if path and os.path.exists(path):
                try:
                    os.remove(path)
                except Exception:
                    pass

    db.delete(product)
    db.commit()
    return {"message": "Product and its images deleted successfully"}

@router.post("/reviews/", status_code=status.HTTP_201_CREATED)
async def create_review(
    body: product_schemas.ReviewCreate, 
    db: Session = Depends(get_db),
):
    """Add a new review for a specific product by a customer"""
    
    product = db.query(models.Product).filter(models.Product.id == body.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    new_review = models.Review(
        product_id=body.product_id,
        rating=body.rating,
        comment=body.comment,
        user_id=1 # Default user ID
    )

    try:
        db.add(new_review)
        db.commit()
        db.refresh(new_review)
        return {"message": "Review added successfully", "review": new_review.id}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to add review")