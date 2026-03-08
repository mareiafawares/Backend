from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database.connection import engine, get_db
from database import models
from routers import users, auth
from schemas.user_schemas import UserLoginSchema
from utils import verify_password


models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Device Hub API",
    description="Backend API for Device Hub application",
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(auth.router, prefix="/auth", tags=["Auth"])

@app.post("/auth/login", tags=["Auth"])
def login(user_credentials: UserLoginSchema, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == user_credentials.email).first()
    
    if not user or not verify_password(user_credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    return {
        "access_token": "token_placeholder", 
        "token_type": "bearer",
        "role": user.role
    }

@app.get("/")
def root():
    return {
        "message": "Welcome to Device Hub API",
        "status": "running",
        "docs": "/docs"
    }