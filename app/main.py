import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from database.connection import engine
from database import models


from routers import users, auth, admin, products_router, orders_router 


models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Device Hub API")



if not os.path.exists("static/products"):
    os.makedirs("static/products")


app.mount("/static", StaticFiles(directory="static"), name="static")



app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(admin.router, prefix="/admin", tags=["Admin Management"])


app.include_router(products_router.router, prefix="/products", tags=["Products Management"])


app.include_router(orders_router.router, prefix="/orders", tags=["Orders Management"])

@app.get("/")
def root():
    return {"message": "API is running successfully"}