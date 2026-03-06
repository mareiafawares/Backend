from fastapi import FastAPI
from .database.connection import engine
from .database import models
from .routers import users, auth

models.Base.metadata.create_all(bind=engine)
app = FastAPI(
    title="Device Hub API",
    description="Backend API for Device Hub application",
    version="1.0.0",
)
app.include_router(users.router ,prefix="/users", tags=["Users"])
app.include_router(auth.router, prefix="/auth", tags=["Auth"])

@app.get("/")
def root():
    return {"message": "Welcome to Device Hub API",
            "status": "running",
            "docs": "/docs"
            }