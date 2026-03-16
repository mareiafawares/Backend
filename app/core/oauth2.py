from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Union
from app.database import connection, models
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

SECRET_KEY = "your_secret"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days for Flutter app

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login", auto_error=True)


class AdminUser:
    """Minimal user-like object for admin (no DB row). Same shape as User for API."""
    id = 0
    email = "mareiafawares@gmail.com"
    username = "Maria Fawares"
    role = "admin"
    shops = []


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(connection.get_db),
) -> Union[models.User, AdminUser]:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        sub = payload.get("sub")
        email = payload.get("email")
        role = payload.get("role")
        if email is None and sub is None:
            raise credentials_exception
        # Admin user (no DB record). sub is string per JWT spec.
        if role == "admin" and (sub == 0 or sub == "0"):
            return AdminUser()
        user = db.query(models.User).filter(models.User.email == email).first()
        if user is None:
            raise credentials_exception
        return user
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token. Please login again.",
            headers={"WWW-Authenticate": "Bearer"},
        )


def require_admin(current_user: Union[models.User, AdminUser] = Depends(get_current_user)):
    if getattr(current_user, "role", None) != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin only")
    return current_user