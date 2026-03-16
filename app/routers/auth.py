from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import connection, models
from app.schemas import user_schemas
from app.utils import verify_password, hash_password
from app.core.oauth2 import create_access_token, get_current_user, AdminUser

router = APIRouter(tags=["Authentication"])

ADMIN_EMAIL = "mareiafawares@gmail.com"
ADMIN_PASSWORD = "mareia2003"


def _user_to_response(user, access_token: str):
    """Build login/me response: token + user fields for Flutter."""
    is_admin = isinstance(user, AdminUser)
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": user.role,
        "username": user.username,
        "id": user.id,
        "shops": list(user.shops) if not is_admin else [],
    }


@router.post("/login")
def login(
    body: user_schemas.UserLogin,
    db: Session = Depends(connection.get_db),
):
    """Login with JSON body: {"email": "...", "password": "..."}."""
    if body.email == ADMIN_EMAIL and body.password == ADMIN_PASSWORD:
        token = create_access_token(
            data={"sub": "0", "email": ADMIN_EMAIL, "role": "admin"}
        )
        return _user_to_response(AdminUser(), token)

    user = db.query(models.User).filter(models.User.email == body.email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    if not verify_password(body.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Password incorrect")

    token = create_access_token(
        data={"sub": str(user.id), "email": user.email, "role": user.role}
    )
    return _user_to_response(user, token)


@router.get("/me")
def me(current_user=Depends(get_current_user)):
    """Return current user from Bearer token. Use in Flutter to restore session."""
    if isinstance(current_user, AdminUser):
        return {
            "id": current_user.id,
            "username": current_user.username,
            "email": current_user.email,
            "role": current_user.role,
            "shops": [],
        }
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "role": current_user.role,
        "shops": [
            {"id": s.id, "name": s.name, "description": s.description, "image_url": s.image_url, "is_approved": s.is_approved, "has_shop_request": s.has_shop_request, "owner_id": s.owner_id}
            for s in current_user.shops
        ],
    }

@router.post("/signup", status_code=status.HTTP_201_CREATED)
def signup(user_data: user_schemas.UserCreate, db: Session = Depends(connection.get_db)):
    existing_user = db.query(models.User).filter(models.User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_pwd = hash_password(user_data.password)

    new_user = models.User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_pwd,
        role=user_data.role
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    token = create_access_token(
        data={"sub": str(new_user.id), "email": new_user.email, "role": new_user.role}
    )
    return _user_to_response(new_user, token)