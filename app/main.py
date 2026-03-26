import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.database.connection import engine
from app.database import models


from app.routers import (
    users, 
    auth, 
    admin, 
    products_router, 
    orders_router, 
    upload, 
    shops,
    favorites  
)


models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Device Hub API",
    description="Backend for Device Hub Mobile Application",
    version="1.0.0"
)


directories = [
    "static/products", 
    "static/uploads/images", 
    "static/uploads/shops",
    "uploads"
]
for directory in directories:
    if not os.path.exists(directory):
        os.makedirs(directory)


app.mount("/static", StaticFiles(directory="static"), name="static")

if os.path.exists("uploads"):
    app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(shops.router, prefix="/api/shops", tags=["Shops Management"])
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(admin.router, prefix="/admin", tags=["Admin Management"])
app.include_router(products_router.router, prefix="/products", tags=["Products Management"])
app.include_router(orders_router.router, prefix="/orders", tags=["Orders Management"])
app.include_router(upload.router, prefix="/upload", tags=["Uploads"])

app.include_router(favorites.router, prefix="/api", tags=["Favorites Management"])

@app.get("/")
def root():
    return {
        "status": "online",
        "message": "Device Hub API is running smoothly",
        "docs": "/docs" 
    }