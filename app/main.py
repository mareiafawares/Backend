from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database.connection import engine
from database import models
# 1. أضيفي استيراد ملف الـ admin من مجلد الـ routers
from routers import users, auth, admin 

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Device Hub API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/users", tags=["Users"])

# 2. أضيفي هذا السطر لربط مسارات الأدمن بالسيرفر
app.include_router(admin.router, prefix="/admin", tags=["Admin Management"])

@app.get("/")
def root():
    return {"message": "API is running successfully"}