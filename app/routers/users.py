from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import connection, models
from ..schemas import user_schemas
from ..core import security
from ..schemas.user_schemas import UserCreate, UserOut

router = APIRouter(prefix="/users", tags=["Users"])

def create_user(user: user_schemas.UserCreate, db: Session = Depends(connection.get_db)):
  hashed_pwd = security.hash_password(user.password) 
  user.password = hashed_pwd

  new_user = models.User(**user.dict())
  db.add(new_user)
  db.commit()
  db.refresh(new_user)
  return new_user
    
