from sqlalchemy.orm import Session
from fastapi.exceptions import HTTPException
from fastapi import status
from book.crud import get_object
from news.models import News
from news.schema import NewsSchema, UpdateNewsSchema


def create_news(session: Session, data: NewsSchema):
    news = News(title=data.title, image=data.image)
    session.add(news)
    session.commit()
    session.refresh(news)
    return news


def update_news(session: Session, data: UpdateNewsSchema, news_id: int):
    news = get_object(session, news_id, News)
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(news, key, value)
    session.commit()
    session.refresh(news)
    return news


def news_detail(session: Session, news_id: int):
    return get_object(session, news_id, News)


def news_list(session: Session):
    return session.query(News).order_by(News.id.desc()).all()


def news_delete(session: Session, news_id: int):
    news = get_object(session, news_id, News)
    session.delete(news)
    session.commit()
    return {"msg": "News deleted", "status": status.HTTP_204_NO_CONTENT, "data": None}