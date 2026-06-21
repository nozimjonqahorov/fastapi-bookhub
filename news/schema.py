from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class NewsSchema(BaseModel):
    title: str = Field(max_length=120)
    image: Optional[str] = None

    model_config = {"from_attributes": True}


class UpdateNewsSchema(BaseModel):
    title: Optional[str] = None
    image: Optional[str] = None

    model_config = {"from_attributes": True}


class NewsResponseSchema(BaseModel):
    id: int
    title: str
    image: Optional[str] = None
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}