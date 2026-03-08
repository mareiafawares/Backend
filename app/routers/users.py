from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from schemas import user_schemas 
from database import models, connection
from utils import hash_password 

router = APIRouter()

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
           
            role=user.role.value if hasattr(user.role, 'value') else user.role  
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user

    except Exception as e:
        db.rollback() 
        print(f"Error occurred: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error during user creation")