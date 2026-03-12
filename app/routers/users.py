from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from schemas import user_schemas 
from database import models, connection
from utils import hash_password 

# تعريف الراوتر
router = APIRouter(tags=["Users"])

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=user_schemas.UserOut)
def create_user(user: user_schemas.UserCreate, db: Session = Depends(connection.get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    try:
        hashed_pass = hash_password(user.password)
        new_user = models.User(
            username=user.username,
            email=user.email,
            hashed_password=hashed_pass,
            role=user.role
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# الدالة السحرية: إضافة متجر جديد للقائمة
@router.post("/create-shop/{user_id}", response_model=user_schemas.UserOut)
def create_shop_request(
    user_id: int, 
    shop_data: user_schemas.ShopCreateRequest, 
    db: Session = Depends(connection.get_db)
):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    try:
        # إنشاء سطر جديد تماماً في جدول المتاجر
        new_shop = models.Shop(
            name=shop_data.shop_name,
            description=shop_data.shop_description,
            owner_id=user_id,
            is_approved=False,
            has_shop_request=True
        )

        db.add(new_shop)
        db.commit()
        db.refresh(user) # لتحديث قائمة المتاجر عند اليوزر
        return user 

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to submit shop request")