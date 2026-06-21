from db import Base
from sqlalchemy import Column, Integer, String, DateTime, func

class News(Base):
    __tablename__ = 'news'
    id = Column(Integer, primary_key=True)
    title = Column(String(120))
    image = Column(String(120), nullable=True)
    created_at = Column(DateTime, default=func.now())