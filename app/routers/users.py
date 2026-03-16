from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas import user_schemas
from app.database import models, connection
from app.utils import hash_password
from app.core.oauth2 import get_current_user

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



@router.post("/create-shop", response_model=user_schemas.UserOut)
async def create_shop_request(
    body: user_schemas.ShopCreateRequest,
    db: Session = Depends(connection.get_db),
    current_user=Depends(get_current_user),
):
    """Create shop with JSON body: {"shop_name": "...", "shop_description": "...", "image_url": "https://..." optional}."""
    if getattr(current_user, "role", None) == "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admins cannot create shops")
    user_id = current_user.id
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    try:
        new_shop = models.Shop(
            name=body.shop_name,
            description=body.shop_description,
            image_url=body.image_url,
            owner_id=user_id,
            is_approved=False,
            has_shop_request=True,
        )
        db.add(new_shop)
        db.commit()
        db.refresh(user)
        return user
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error")