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
    
   
    favorites = relationship("Favorite", back_populates="user", cascade="all, delete-orphan")


class Shop(Base):
    __tablename__ = "shops"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    image_url = Column(String, nullable=True)
    is_approved = Column(Boolean, default=False)
    has_shop_request = Column(Boolean, default=True)

    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="shops")
    
    products = relationship("Product", back_populates="shop", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="shop")


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    description = Column(String, nullable=True)
    price = Column(Float, nullable=False)
    discount_price = Column(Float, nullable=True)
    stock_quantity = Column(Integer, default=0)
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
    order_items = relationship("OrderItem", back_populates="product")
    
   
    favorited_by = relationship("Favorite", back_populates="product", cascade="all, delete-orphan")


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
    rating = Column(Integer, default=5, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user_id = Column(Integer, ForeignKey("users.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    
    user = relationship("User", back_populates="reviews")
    product = relationship("Product", back_populates="reviews")



class Favorite(Base):
    __tablename__ = "favorites"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

   
    user = relationship("User", back_populates="favorites")
    product = relationship("Product", back_populates="favorited_by")


class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    
    full_name = Column(String, nullable=False)
    phone_number = Column(String, nullable=False)
    city = Column(String, nullable=False)
    address_details = Column(Text, nullable=False)
    delivery_notes = Column(Text, nullable=True)
    
    total_price = Column(Float, nullable=False)
    status = Column(String, default="Pending") 
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    buyer_id = Column(Integer, ForeignKey("users.id"))
    buyer = relationship("User", back_populates="orders")

    shop_id = Column(Integer, ForeignKey("shops.id"))
    shop = relationship("Shop", back_populates="orders")
    
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")


class OrderItem(Base):
    __tablename__ = "order_items"
    id = Column(Integer, primary_key=True, index=True)
    
    order_id = Column(Integer, ForeignKey("orders.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    
    quantity = Column(Integer, nullable=False)
    price_at_purchase = Column(Float, nullable=False)
    product_name = Column(String, nullable=True) 
    product_image = Column(String, nullable=True) 

    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")