from fastapi import FastAPI
from .database import connection, models
from .routers import users, auth

models.Base.metadata.create_all(bind=connection.engine)
app = FastAPI()
app.include_router(users.router)
app.include_router(auth.router)

@app.get("/")
def root():
    return {"message": "Welcome to the FastAPI application!"}