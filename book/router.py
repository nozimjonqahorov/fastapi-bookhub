from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from db import get_db
from permissions import get_current_user, require_admin
from users.models import User
import book.crud as crud
import book.schema as schema

router = APIRouter()


@router.post('/create-author')
def create_author_router(data: schema.AuthorSchema, session: Session = Depends(get_db), admin: User = Depends(require_admin)):
    return crud.create_author(session, data)


@router.get('/detail-author/{author_id}', response_model=schema.AuthorResponseSchema)
def detail_author_router(author_id: int, session: Session = Depends(get_db)):
    return crud.author_detail(session, author_id)


@router.get('/list-author/', response_model=list[schema.AuthorResponseSchema])
def list_author_router(session: Session = Depends(get_db)):
    return crud.author_list(session)


@router.patch('/update-author/{author_id}')
def update_author_router( author_id: int, data: schema.UpdateAuthorSchema, session: Session = Depends(get_db), admin: User = Depends(require_admin)):
    return crud.update_author(session, data, author_id)


@router.delete('/delete-author/{author_id}')
def delete_author_router(author_id: int, session: Session = Depends(get_db), admin: User = Depends(require_admin)):
    return crud.author_delete(session, author_id)



@router.post('/create-category')
def create_category_router(data: schema.CategorySchema, session: Session = Depends(get_db), admin: User = Depends(require_admin)):
    return crud.create_category(session, data)


@router.get('/detail-category/{category_id}', response_model=schema.CategoryResponseSchema)
def detail_category_router(category_id: int, session: Session = Depends(get_db)):
    return crud.category_detail(session, category_id)


@router.get('/list-category/', response_model = list[schema.CategoryResponseSchema])
def list_category_router(session: Session = Depends(get_db)):
    return crud.category_list(session)


@router.patch('/update-category/{category_id}')
def update_category_router(category_id: int, data: schema.UpdateCategorySchema, session: Session = Depends(get_db), admin: User = Depends(require_admin)):
    return crud.update_category(session, data, category_id)


@router.delete('/delete-category/{category_id}')
def delete_category_router(category_id: int, session: Session = Depends(get_db), admin: User = Depends(require_admin)):
    return crud.category_delete(session, category_id)


@router.post('/create-book')
def create_book_router(
    data: schema.BookSchema,
    session: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return crud.create_book(session, data, current_user.id)


@router.get('/detail-book/{book_id}', response_model=schema.BookDetailResponseSchema)
def detail_book_router(book_id: int, session: Session = Depends(get_db)):
    return crud.book_detail(session, book_id)


@router.get('/list-book/', response_model=list[schema.BookShortResponseSchema])
def list_book_router(
    title: str = Query(default=None),
    author_id: int = Query(default=None),
    category_id: int = Query(default=None),
    ordering: str = Query(default=None),
    limit: int = Query(default=20),
    offset: int = Query(default=0),
    session: Session = Depends(get_db),
):
    return crud.book_list(session, title, author_id, category_id, ordering, limit, offset)


@router.patch('/update-book/{book_id}')
def update_book_router(
    book_id: int,
    data: schema.UpdateBookSchema,
    session: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    return crud.update_book(session, data, book_id)


@router.delete('/delete-book/{book_id}')
def delete_book_router(
    book_id: int,
    session: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    return crud.book_delete(session, book_id)


@router.post('/create-review')
def create_review_router(
    data: schema.ReviewSchema,
    session: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return crud.create_review(session, data, current_user.id)


@router.patch('/update-review/{review_id}')
def update_review_router(
    review_id: int,
    data: schema.UpdateReviewSchema,
    session: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return crud.update_review(session, data, review_id, current_user)


@router.get('/book/reviews/list/{book_id}', response_model= list[schema.ReviewResponseSchema])
def review_list_router(
    book_id: int,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    session: Session = Depends(get_db),
):
    return crud.review_list(session, book_id, limit, offset)


@router.delete('/delete-review/{review_id}')
def delete_review_router(
    review_id: int,
    session: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return crud.delete_review(session, review_id, current_user)


@router.post('/wishlist/')
def toggle_wishlist_router(
    data: schema.WishlistSchema,
    session: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return crud.toggle_wishlist(session, data, current_user.id)


@router.get('/wishlist/my', response_model=list[schema.WishlistResponseSchema])
def wishlist_list_router(
    session: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return crud.wishlist_list(session, current_user.id)
