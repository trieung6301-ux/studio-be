from sqlalchemy import Column, Integer, String, LargeBinary, Float, Boolean
from database import Base

class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(50))
    last_name = Column(String(50))
    username = Column(String(50), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)
    email = Column(String(120), unique=True, index=True, nullable=False)
    role = Column(String(20), default="user")
    avatar = Column(String(255), nullable=True)

class Product(Base):
    __tablename__ = "product"

    id = Column(Integer, primary_key=True, index=True)
    product_name = Column(String(100), nullable=False)
    product_desc = Column(String(255))
    product_type = Column(String(50))
    product_image = Column(LargeBinary)
    product_price = Column(Float, nullable=False)
    deleted = Column(Boolean, default=False)

class Schedule(Base):
    __tablename__ = "schedule"

    id = Column(Integer, primary_key=True, index=True)
    day_of_week = Column(String(10), nullable=False)
    exercise_name = Column(String(100), nullable=False)
    sets = Column(Integer, nullable=False)
    reps = Column(Integer, nullable=False)
    weight = Column(Float, nullable=True)
    deleted = Column(Boolean, default=False)