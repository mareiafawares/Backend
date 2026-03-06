from sqlalchemy import Column, Integer ,String ,Float, Boolean,ForeignKey,Enum
from sqlalchemy.orm import relationship
import enum
from .base_class import Base

class UserRole(str, enum.Enum):
    admin ="admin"
    seller = "seller"
    customer = "customer"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True ,nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String , nullable=False)
    role = Column(String,default=UserRole.customer)

    products= relationship("Product", back_populates="owner")

    class Product(Base):
        __tablename__ = "products"

        id = Column(Integer, primary_key=True, index=True)
        name = Column(String, index=True, nullable=False)
        is_approved = Column(Boolean, default=False)
        price = Column(Float, nullable=False)
        image_url = Column(String , nullable=True)
        is_new = Column(Boolean, default=False)
        owner_id = Column(Integer, ForeignKey("users.id"))
        owner = relationship("User", back_populates="products")