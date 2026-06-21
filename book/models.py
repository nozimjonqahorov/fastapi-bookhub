from db import Base
from sqlalchemy import Column, String, Integer, Text, ForeignKey, func, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship

class Author(Base):
    __tablename__ = 'authors'
    
    id = Column(Integer, primary_key=True)
    fullname = Column(String(120))
    created_at = Column(DateTime, default=func.now())
    
    books = relationship('Book', back_populates='author')


class Category(Base):
    __tablename__ = 'categories'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(120))
    created_at = Column(DateTime, default=func.now())
    
    books = relationship('Book', back_populates='category')


class Book(Base):
    __tablename__ = 'books'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(120))
    image = Column(String(120), nullable=True)
    desc = Column(Text, nullable=True)
    author_id = Column(Integer, ForeignKey('authors.id', ondelete='CASCADE'))
    category_id = Column(Integer, ForeignKey('categories.id', ondelete='CASCADE'))
    created_at = Column(DateTime, default=func.now())

    
    author = relationship('Author', back_populates='books')
    category = relationship('Category', back_populates='books')
    reviews = relationship('Review', back_populates='book')
    
    
class Review(Base):
    __tablename__ = 'reviews'
    
    id = Column(Integer, primary_key=True)
    summary = Column(Text, nullable=False)
    rating = Column(Integer)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'))
    book_id = Column(Integer, ForeignKey('books.id', ondelete='CASCADE'))
    created_at = Column(DateTime, default=func.now())

    user = relationship('User', back_populates='reviews')
    book = relationship('Book', back_populates='reviews')
    
class Wishlist(Base):
    __tablename__ = 'wishlists'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'))
    book_id = Column(Integer, ForeignKey('books.id', ondelete='CASCADE'))
    created_at = Column(DateTime, default=func.now())


    book = relationship('Book')
    user = relationship('User', back_populates='wishlists')
    
    __table_args__ = (
        UniqueConstraint('user_id', 'book_id', name='uq_user_book'),
    )

