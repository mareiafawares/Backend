from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from .connection import Base 


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="customer") 

   
    shops = relationship("Shop", back_populates="owner")
    products = relationship("Product", back_populates="owner")


class Shop(Base):
    __tablename__ = "shops"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    is_approved = Column(Boolean, default=False)
    has_shop_request = Column(Boolean, default=True)
    
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="shops")
    
   
    products = relationship("Product", back_populates="shop", cascade="all, delete-orphan")


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    description = Column(String, nullable=True)
    price = Column(Float, nullable=False)
    discountPrice = Column(Float, nullable=True) 
    stockQuantity = Column(Integer, default=0)   
    imageUrl = Column(String, nullable=True)     
    status = Column(String, default="Available")
    category = Column(String, nullable=True)
    is_new = Column(Boolean, default=True)
    is_approved = Column(Boolean, default=False)

    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="products")
    
    shop_id = Column(Integer, ForeignKey("shops.id"))
    shop = relationship("Shop", back_populates="products")