from app.database import models,connection
from app.core import security
from sqlalchemy.orm import Session

def create_initial_admin():
    db=next(connection.get_db())

    admin_exists = db.query(models.User).filter(models.User.email == "admin@devicehub.com").first()
    if not admin_exists:
        hashed_pass = security.hash_password("admin123")
        new_admin = models.User(
            username="admin",
            email="admin@devicehub.com",
            hashed_password=hashed_pass,
            role="admin")
        
        db.add(new_admin)
        db.commit()
        print("✅ Success: Admin user created successfully!")
        print("Email: admin@devicehub.com | Password: admin123")
    else:
        print("⚠️ Admin user already exists. No new admin created.")
if __name__ == "__main__":
    create_initial_admin()