
from pydantic import BaseModel, ConfigDict, Field, AnyUrl
from typing import Optional, List
from datetime import datetime

class AuthorSchema(BaseModel):
    fullname: str = Field(max_length=120)

    model_config = {"from_attributes": True}

class AuthorResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id : int
    fullname: str
    created_at: Optional[datetime] = None

class UpdateAuthorSchema(BaseModel):
    fullname: Optional[str] = None

    model_config = {"from_attributes": True}

class CategorySchema(BaseModel):
    title : str = Field(max_length=100)

    model_config = {"from_attributes": True}
    
class UpdateCategorySchema(BaseModel):
    title: Optional[str] = None

    model_config = {"from_attributes": True}
    

class CategoryResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id : int
    title: str
    created_at: Optional[datetime] = None

class BookSchema(BaseModel):
    title : str = Field(min_length=1, max_length=120)
    image : Optional[AnyUrl] = None
    desc : Optional[str] = Field(default=None, max_length=2000)
    author_id : int
    category_id : int

    model_config = {"from_attributes": True}
    
    
class UpdateBookSchema(BaseModel):
    title : Optional[str] = None
    image : Optional[str] = None
    desc : Optional[str] = None
    author_id : Optional[int] = None
    category_id : Optional[int] = None

    model_config = {"from_attributes": True}
    
class BookShortResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    slug: str
    image: Optional[AnyUrl] = None
    desc: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    author: Optional[AuthorResponseSchema] = None
    category: Optional[CategoryResponseSchema] = None
    created_by: Optional[int] = None
    avg_rating: Optional[float] = None
    reviews_count: int = 0


class ReviewResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    summary: str
    rating: int
    created_at: Optional[datetime] = None
    username: Optional[str] = None


class BookDetailResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    slug: str
    image: Optional[AnyUrl] = None
    desc: Optional[str] = None
    author: AuthorResponseSchema
    category: CategoryResponseSchema
    avg_rating: Optional[float] = None
    reviews_count: int = 0
    created_by: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    reviews: List[ReviewResponseSchema] = []


class ReviewSchema(BaseModel):
    summary: str = Field(min_length=10, max_length=1500)
    rating: int = Field(ge=1, le=10)
    book_id: int

    model_config = {"from_attributes": True}
    
    
class UpdateReviewSchema(BaseModel):
    summary: Optional[str] = Field(default=None, max_length=1500)
    rating: Optional[int] = Field(default=None, ge=1, le=10)

    model_config = {"from_attributes": True}


class WishlistSchema(BaseModel):
    book_id: int

    model_config = {"from_attributes": True}
        
    
    
class WishlistResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    wishlist_id: int
    book_id: int
    title: str
    image: Optional[str] = None
    
    
    
