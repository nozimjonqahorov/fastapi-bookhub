from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from db import get_db
from permissions import require_admin
from users.models import User
import news.crud as crud
import news.schema as schema

router = APIRouter()


@router.post('/create-news', response_model=schema.NewsResponseSchema)
def create_news_router(
    data: schema.NewsSchema,
    session: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    return crud.create_news(session, data)


@router.get('/detail-news/{news_id}', response_model=schema.NewsResponseSchema)
def detail_news_router(news_id: int, session: Session = Depends(get_db)):
    return crud.news_detail(session, news_id)


@router.get('/list-news/', response_model=list[schema.NewsResponseSchema])
def list_news_router(session: Session = Depends(get_db)):
    return crud.news_list(session)


@router.patch('/update-news/{news_id}', response_model=schema.NewsResponseSchema)
def update_news_router(
    news_id: int,
    data: schema.UpdateNewsSchema,
    session: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    return crud.update_news(session, data, news_id)


@router.delete('/delete-news/{news_id}')
def delete_news_router(
    news_id: int,
    session: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    return crud.news_delete(session, news_id)