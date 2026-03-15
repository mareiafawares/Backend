import os
from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form
from sqlalchemy.orm import Session
from schemas import user_schemas 
from database import models, connection

router = APIRouter(tags=["Users"])

@router.post("/create-shop/{user_id}", response_model=user_schemas.UserOut)
async def create_shop_request(
    user_id: int, 
    shopName: str = Form(...),
    shopDescription: str = Form(...),
    image: UploadFile = File(None),
    db: Session = Depends(connection.get_db)
):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    file_path = None
    
    if image:
        upload_dir = "static/uploads/shops"
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir, exist_ok=True)
            
        file_name = f"{user_id}_{image.filename}"
        file_path = os.path.join(upload_dir, file_name).replace("\\", "/")
        
        try:
            with open(file_path, "wb") as buffer:
                content = await image.read()
                buffer.write(content)
        except Exception:
            raise HTTPException(status_code=500, detail="Failed to upload image")

    try:
        new_shop = models.Shop(
            name=shopName,
            description=shopDescription,
            owner_id=user_id,
            image_url=file_path, 
            is_approved=False,
            has_shop_request=True
        )
        
        db.add(new_shop)
        db.commit()
        db.refresh(user) 
        
        return user 
        
    except Exception as e:
        db.rollback()
        
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
            
        raise HTTPException(status_code=500, detail="Could not process shop request")