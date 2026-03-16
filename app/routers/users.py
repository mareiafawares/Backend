import os
from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form
from sqlalchemy.orm import Session
from schemas import user_schemas 
from database import models, connection
from utils import hash_password 

router = APIRouter(tags=["Users"])


@router.post("/register", response_model=user_schemas.UserOut)
def create_user(user: user_schemas.UserCreate, db: Session = Depends(connection.get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_pwd = hash_password(user.password)
    new_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_pwd, 
        role=user.role
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user



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
        os.makedirs(upload_dir, exist_ok=True)
        file_name = f"{user_id}_{image.filename}"
        file_path = os.path.join(upload_dir, file_name).replace("\\", "/")
        
        try:
            with open(file_path, "wb") as buffer:
                content = await image.read()
                buffer.write(content)
        except Exception as e:
            print(f"Image Upload Error: {e}")
            raise HTTPException(status_code=500, detail="Failed to upload image")

    try:
        
        new_shop = models.Shop(
            name=shopName,
            description=shopDescription,
            owner_id=user_id,
            is_approved=False,
            has_shop_request=True
            
        )
        
        db.add(new_shop)
        db.commit()
        db.refresh(user) 
        return user 
        
    except Exception as e:
        db.rollback()
        
        print(f"DATABASE ERROR: {str(e)}")
        
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
            
        
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")