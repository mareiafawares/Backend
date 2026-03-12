from pydantic import BaseModel, EmailStr
from enum import Enum
from typing import Optional, List

# 1. الرتب المتاحة في النظام
class UserRegisterRole(str, Enum):
    admin = "admin"
    seller = "seller"
    customer = "customer"

# 2. سكيما المتجر (تفاصيل كل محل)
class ShopOut(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    is_approved: bool
    has_shop_request: bool
    owner_id: int

    class Config:
        from_attributes = True

# 3. النموذج الأساسي للمستخدم
class UserBase(BaseModel):
    username: str
    email: EmailStr

# 4. تسجيل مستخدم جديد
class UserCreate(UserBase):
    password: str
    role: UserRegisterRole

# 5. تسجيل الدخول
class UserLoginSchema(BaseModel):
    email: EmailStr
    password: str

# 6. طلب إنشاء متجر
class ShopCreateRequest(BaseModel):
    shop_name: str
    shop_description: str

# 7. النموذج النهائي للمستخدم (يرسل قائمة متاجر)
class UserOut(BaseModel):
    id: int
    username: str
    email: EmailStr
    role: str
    shops: List[ShopOut] = [] # الحل الصحيح للتعدد

    class Config:
        from_attributes = True