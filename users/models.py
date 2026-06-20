from sqlalchemy import String, Column, Integer, func, DateTime
from db import Base


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    first_name = Column(String(30), nullable=False)
    last_name = Column(String(30))
    username = Column(String(50), nullable=False, unique=True, index=True)
    email = Column(String(200), nullable=False, unique=True)
    phone_number = Column(String(13), unique=True, nullable=False)
    password = Column(String(255))



class BlackListToken(Base):
    __tablename__ = 'blacklist_token'
    id = Column(Integer, primary_key=True)
    jti = Column(String, unique=True)
    created_at = Column(DateTime, default=func.now())
