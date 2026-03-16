from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
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
    reviews = relationship("Review", back_populates="user")
    orders = relationship("Order", back_populates="buyer")



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
    status = Column(String, default="Available")
    category = Column(String, nullable=True)
    is_new = Column(Boolean, default=True)
    is_approved = Column(Boolean, default=False)

    
    owner_id = Column(Integer, ForeignKey("users.id"))
    shop_id = Column(Integer, ForeignKey("shops.id"))

   
    owner = relationship("User", back_populates="products")
    shop = relationship("Shop", back_populates="products")

    
    images = relationship("ProductImage", back_populates="product", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="product", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="product")



class ProductImage(Base):
    __tablename__ = "product_images"
    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"))
    
    product = relationship("Product", back_populates="images")



class Review(Base):
    __tablename__ = "reviews"
    id = Column(Integer, primary_key=True, index=True)
    comment = Column(Text, nullable=True)
    rating = Column(Integer, default=5)  
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user_id = Column(Integer, ForeignKey("users.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    
    user = relationship("User", back_populates="reviews")
    product = relationship("Product", back_populates="reviews")



class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    buyer_id = Column(Integer, ForeignKey("users.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    
    buyer = relationship("User", back_populates="orders")
    product = relationship("Product", back_populates="orders")