from sqlalchemy import String, Column, Integer, func, DateTime, Enum
from db import Base
from sqlalchemy.orm import relationship
import enum


class UserRole(str, enum.Enum):
    USER = "user"
    ADMIN = "admin"



class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    first_name = Column(String(30), nullable=False)
    last_name = Column(String(30))
    username = Column(String(50), nullable=False, unique=True, index=True)
    email = Column(String(200), nullable=False, unique=True)
    phone_number = Column(String(13), unique=True, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False)
    password = Column(String(255))

    reviews = relationship('Review', back_populates='user')
    wishlists = relationship('Wishlist', back_populates='user')

class BlackListToken(Base):
    __tablename__ = 'blacklist_token'
    id = Column(Integer, primary_key=True)
    jti = Column(String, unique=True)
    created_at = Column(DateTime, default=func.now())

