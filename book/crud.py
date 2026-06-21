from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from fastapi.exceptions import HTTPException
from fastapi import status

from book.models import Author, Category, Book, Review, Wishlist
from book.schema import (
    AuthorSchema, UpdateAuthorSchema,
    CategorySchema, UpdateCategorySchema,
    BookSchema, UpdateBookSchema,
    ReviewSchema, UpdateReviewSchema,
    WishlistSchema,
)
from users.models import UserRole



def get_object(session, id, model):
    obj = session.query(model).filter(model.id == id).first()
    if not obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={'msg': f"{model.__name__} not found"}
        )
    return obj

def response_model(msg, status_code, data, etc = None):
    if etc:
        return {"msg": msg, "status": status_code, "etc": etc, "data": data}
    return {"msg": msg, "status": status_code, "data": data}

#AUTHOR

def create_author(session: Session, data: AuthorSchema):
    author = Author(fullname=data.fullname)
    session.add(author)
    session.commit()
    session.refresh(author)
    return response_model("Author created", status.HTTP_201_CREATED, author)


def update_author(session: Session, data: UpdateAuthorSchema, author_id: int):
    author = get_object(session, author_id, Author)
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(author, key, value)
    session.commit()
    session.refresh(author)
    return response_model("Author updated", status.HTTP_200_OK, author)


def author_detail(session: Session, author_id: int):
    author = get_object(session, author_id, Author)
    return author


def author_list(session: Session):
    authors = session.query(Author).order_by(Author.id.desc()).all()
    return authors

def author_delete(session: Session, author_id: int):
    author = get_object(session, author_id, Author)
    session.delete(author)
    session.commit()
    return response_model("Author deleted", status.HTTP_204_NO_CONTENT, data=None)


#CATEGORY
def create_category(session: Session, data: CategorySchema):
    category = Category(title=data.title)
    session.add(category)
    session.commit()
    session.refresh(category)
    return response_model("Category created", status.HTTP_201_CREATED, category)

def update_category(session: Session, data: UpdateCategorySchema, category_id: int):
    category = get_object(session, category_id, Category)
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(category, key, value)
    session.commit()
    session.refresh(category)
    return response_model("Category updated", status.HTTP_200_OK, category)


def category_detail(session: Session, category_id: int):
    category = get_object(session, category_id, Category)
    return category


def category_list(session: Session):
    categories = session.query(Category).order_by(Category.id.desc()).all()
    return categories


def category_delete(session: Session, category_id: int):
    category = get_object(session, category_id, Category)
    session.delete(category)
    session.commit()
    return response_model("Category deleted", status.HTTP_204_NO_CONTENT, data=None)


# BOOK 

def create_book(session: Session, data: BookSchema):
    category = get_object(session, data.category_id, Category)
    author = get_object(session, data.author_id, Author)
    book = Book(title = data.title, image = data.image, desc = data.desc, author_id = author.id, category_id = category.id )
    try:
        session.add(book)
        session.commit()
        session.refresh(book)
    except Exception:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"msg": "Book yaratishda ma'lumotlar xato"},
        )

    return response_model("Book created", status.HTTP_201_CREATED, book)


def update_book(session: Session, data: UpdateBookSchema, book_id: int):
    book = get_object(session, book_id, Book)
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(book, key, value)
    session.commit()
    session.refresh(book)
    return response_model("Book updated", status.HTTP_200_OK, book)


def book_detail(session: Session, book_id: int):
    book = (session.query(Book).options(
            joinedload(Book.author),
            joinedload(Book.category),
            joinedload(Book.reviews),
        )
        .filter(Book.id == book_id).first())

    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")

    avg_rating = (
        session.query(func.avg(Review.rating))
        .filter(Review.book_id == book_id)
        .scalar()
    )

    return {
        "id": book.id,
        "title": book.title,
        "image": book.image,
        "desc": book.desc,
        "author": {
            "id": book.author.id,
            "fullname": book.author.fullname,
        },
        "category": {
            "id": book.category.id,
            "title": book.category.title,
        },
        "avg_rating": round(avg_rating, 1) if avg_rating else None,
        "reviews_count": len(book.reviews),
        "reviews": [
            {
                "id":r.id, 
                "summary": r.summary,
                "rating": r.rating,
                "username": r.user.username,
            }
            for r in book.reviews
        ],
    }


def book_delete(session: Session, book_id: int):
    book = get_object(session, book_id, Book)
    session.delete(book)
    session.commit()
    return response_model("Book deleted", status.HTTP_204_NO_CONTENT, data=None)


def book_list(
    session: Session,
    title: str = None,
    author_id: int = None,
    category_id: int = None,
    ordering: str = None,
    limit: int = 20,
    offset: int = 0,
):
    query = session.query(Book).options(joinedload(Book.author), joinedload(Book.category))

    if title:
        query = query.filter(Book.title.ilike(f"%{title}%"))
    if author_id:
        query = query.filter(Book.author_id == author_id)
    if category_id:
        query = query.filter(Book.category_id == category_id)

    if ordering == "title":
        query = query.order_by(Book.title.asc())
    elif ordering == "-title":
        query = query.order_by(Book.title.desc())
    else:
        query = query.order_by(Book.id.desc())

    return query.offset(offset).limit(limit).all()


def create_review(session: Session, data: ReviewSchema, user_id: int):
    review = Review(
        summary=data.summary,
        rating=data.rating,
        book_id=data.book_id,
        user_id=user_id,
    )
    session.add(review)
    session.commit()
    session.refresh(review)
    return response_model("Review created", status.HTTP_201_CREATED, review)


def update_review(session: Session, data: UpdateReviewSchema, review_id: int, current_user):
    review = get_object(session, review_id, Review)

    if review.user_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"msg": "Bu sharhni tahrirlashga ruxsatingiz yo'q"},
        )

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(review, key, value)

    session.commit()
    session.refresh(review)
    return response_model("Review updated", status.HTTP_200_OK, review)


def review_list(session: Session, book_id: int):
    reviews = session.query(Review).filter(Review.book_id == book_id).all()
    result = []
    for r in reviews:
        result.append({
            "id": r.id,
            "summary": r.summary,
            "rating": r.rating,
            "username": r.user.username,
            "created_at": r.created_at,
        })
    return result


def delete_review(session: Session, review_id: int, current_user):
    review = get_object(session, review_id, Review)

    if review.user_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"msg": "Bu sharhni o'chirishga ruxsatingiz yo'q"},
        )

    session.delete(review)
    session.commit()
    return response_model("Review deleted", status.HTTP_204_NO_CONTENT, data=None)


def toggle_wishlist(session: Session, data: WishlistSchema, user_id: int):
    existing = (
        session.query(Wishlist)
        .filter(Wishlist.book_id == data.book_id, Wishlist.user_id == user_id)
        .first()
    )
    if existing:
        session.delete(existing)
        session.commit()
        return response_model("Wishlist deleted", status.HTTP_204_NO_CONTENT, data=None)

    wishlist = Wishlist(book_id=data.book_id, user_id=user_id)
    session.add(wishlist)
    session.commit()
    session.refresh(wishlist)
    return response_model("Wishlist created", status.HTTP_201_CREATED, wishlist)


def wishlist_list(session: Session, user_id: int):
    wishlist_books = session.query(Wishlist).filter(Wishlist.user_id == user_id).all()
    return [
        {
            "wishlist_id": item.id,
            "book_id": item.book_id,
            "title": item.book.title,
            "image": item.book.image,
        }
        for item in wishlist_books
    ]

