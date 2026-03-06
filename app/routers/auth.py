from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from ..database import connection, models
from ..core import oauth2, security

router = APIRouter(tags=["Authentication"])

@router.post("/login")
def login(user_credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(connection.get_db)):
    
    
    user = db.query(models.User).filter(models.User.email == user_credentials.username).first()
    
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid Credentials"
        )
    
    
    if not security.verify_password(user_credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid Credentials"
        )
    
    
    access_token = oauth2.create_access_token(data={
        "user_id": user.id,
        "email": user.email,
        "role": user.role
    })
    
    return {"access_token": access_token, "token_type": "bearer"}