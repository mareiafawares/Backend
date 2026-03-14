from passlib.context import CryptContext


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str):
    """تحويل كلمة المرور العادية إلى نص مشفر"""
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    """التأكد من أن كلمة المرور المدخلة تطابق النص المشفر في قاعدة البيانات"""
    return pwd_context.verify(plain_password, hashed_password)