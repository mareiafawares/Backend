from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from database import connection, models
from schemas import user_schemas 
from utils import verify_password, hash_password 


router = APIRouter(tags=["Authentication"])

ADMIN_EMAIL = "mareiafawares@gmail.com"
ADMIN_PASSWORD = "mareia2003"

@router.post("/login")
def login(user_credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(connection.get_db)):
   
    if user_credentials.username == ADMIN_EMAIL and user_credentials.password == ADMIN_PASSWORD:
        return {
            "access_token": "admin_master_token_2026",
            "token_type": "bearer",
            "role": "admin",
            "username": "Maria Fawares",
            "id": 0,
            "shops": [] 
        }

    
    user = db.query(models.User).filter(models.User.email == user_credentials.username).first()
    
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

   
    if not verify_password(user_credentials.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Password incorrect")

   
    return {
        "access_token": f"session_{user.id}",
        "token_type": "bearer",
        "role": user.role,
        "username": user.username,
        "id": user.id,
        "shops": user.shops 
    }

@router.post("/signup", status_code=status.HTTP_201_CREATED)
def signup(user_data: user_schemas.UserCreate, db: Session = Depends(connection.get_db)):
    existing_user = db.query(models.User).filter(models.User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_pwd = hash_password(user_data.password)

    new_user = models.User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_pwd,
        role=user_data.role
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {"status": "success", "user_id": new_user.id}