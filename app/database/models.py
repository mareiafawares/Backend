from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship
import enum
from .base_class import Base

# تعريف الأدوار
class UserRole(str, enum.Enum):
    admin = "admin"
    seller = "seller"
    customer = "customer"

# 1. جدول المستخدمين
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default=UserRole.customer)

    # الربط الجديد: المستخدم الواحد له "قائمة" متاجر و"قائمة" منتجات
    shops = relationship("Shop", back_populates="owner")
    products = relationship("Product", back_populates="owner")

# 2. جدول المتاجر الجديد (هنا الحل الصحيح 100%)
class Shop(Base):
    __tablename__ = "shops"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    is_approved = Column(Boolean, default=False)      # هل وافق الأدمن على هذا المتجر؟
    has_shop_request = Column(Boolean, default=True)  # هل الطلب قيد الانتظار؟
    
    # ربط المتجر بصاحبه
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="shops")

# 3. جدول المنتجات
class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    is_approved = Column(Boolean, default=False)
    price = Column(Float, nullable=False)
    image_url = Column(String, nullable=True)
    is_new = Column(Boolean, default=False)
    
    # ربط المنتج بصاحبه (البائع)
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="products")