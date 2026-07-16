import re
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
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


def slugify(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = re.sub(r"-+", "-", value).strip("-")
    return value

#AUTHOR

def create_author(session: Session, data: AuthorSchema):
    existing_author = session.query(Author).filter(Author.fullname.ilike(data.fullname.strip())).first()
    if existing_author:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"msg": "Bu muallif allaqachon mavjud"},
        )

    author = Author(fullname=data.fullname.strip())
    session.add(author)
    session.commit()
    session.refresh(author)
    return response_model("Author created", status.HTTP_201_CREATED, author)


def update_author(session: Session, data: UpdateAuthorSchema, author_id: int):
    author = get_object(session, author_id, Author)
    payload = data.model_dump(exclude_unset=True)
    if payload.get("fullname"):
        existing_author = (
            session.query(Author)
            .filter(Author.fullname.ilike(payload["fullname"].strip()), Author.id != author.id)
            .first()
        )
        if existing_author:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"msg": "Bu muallif nomi allaqachon foydalanilgan"},
            )

    for key, value in payload.items():
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
    existing_category = session.query(Category).filter(Category.title.ilike(data.title.strip())).first()
    if existing_category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"msg": "Bu kategoriya allaqachon mavjud"},
        )

    category = Category(title=data.title.strip())
    session.add(category)
    session.commit()
    session.refresh(category)
    return response_model("Category created", status.HTTP_201_CREATED, category)


def update_category(session: Session, data: UpdateCategorySchema, category_id: int):
    category = get_object(session, category_id, Category)
    payload = data.model_dump(exclude_unset=True)
    if payload.get("title"):
        existing_category = (
            session.query(Category)
            .filter(Category.title.ilike(payload["title"].strip()), Category.id != category.id)
            .first()
        )
        if existing_category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"msg": "Bu kategoriya nomi allaqachon foydalanilgan"},
            )

    for key, value in payload.items():
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

def create_book(session: Session, data: BookSchema, user_id: int):
    category = get_object(session, data.category_id, Category)
    author = get_object(session, data.author_id, Author)

    existing_book = (
        session.query(Book)
        .filter(Book.title.ilike(data.title.strip()), Book.author_id == author.id)
        .first()
    )
    if existing_book:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"msg": "Bu nomdagi kitob muallif uchun allaqachon mavjud"},
        )

    slug = slugify(f"{data.title}-{author.fullname}")
    book = Book(
        title=data.title.strip(),
        slug=slug,
        image=data.image,
        desc=data.desc,
        author_id=author.id,
        category_id=category.id,
        created_by=user_id,
    )
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
    payload = data.model_dump(exclude_unset=True)

    if payload.get("author_id"):
        get_object(session, payload["author_id"], Author)
    if payload.get("category_id"):
        get_object(session, payload["category_id"], Category)

    new_title = payload.get("title", book.title)
    new_author_id = payload.get("author_id", book.author_id)

    duplicate_book = (
        session.query(Book)
        .filter(
            Book.title.ilike(new_title.strip()),
            Book.author_id == new_author_id,
            Book.id != book.id,
        )
        .first()
    )
    if duplicate_book:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"msg": "Bu nomdagi kitob muallif uchun allaqachon mavjud"},
        )

    if payload.get("title") or payload.get("author_id"):
        target_title = new_title.strip()
        target_author = session.query(Author).filter(Author.id == new_author_id).first()
        book.slug = slugify(f"{target_title}-{target_author.fullname}")

    for key, value in payload.items():
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
        "slug": book.slug,
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
        "created_by": book.created_by,
        "created_at": book.created_at,
        "updated_at": book.updated_at,
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

    books = query.offset(offset).limit(limit).all()
    book_ids = [book.id for book in books]

    avg_ratings = {}
    review_counts = {}
    if book_ids:
        avg_data = (
            session.query(Review.book_id, func.avg(Review.rating))
            .filter(Review.book_id.in_(book_ids))
            .group_by(Review.book_id)
            .all()
        )
        count_data = (
            session.query(Review.book_id, func.count(Review.id))
            .filter(Review.book_id.in_(book_ids))
            .group_by(Review.book_id)
            .all()
        )
        avg_ratings = {book_id: avg for book_id, avg in avg_data}
        review_counts = {book_id: count for book_id, count in count_data}

    result = []
    for book in books:
        result.append({
            "id": book.id,
            "title": book.title,
            "slug": book.slug,
            "image": book.image,
            "desc": book.desc,
            "created_at": book.created_at,
            "updated_at": book.updated_at,
            "created_by": book.created_by,
            "author": {
                "id": book.author.id,
                "fullname": book.author.fullname,
            } if book.author else None,
            "category": {
                "id": book.category.id,
                "title": book.category.title,
            } if book.category else None,
            "avg_rating": round(avg_ratings.get(book.id), 1) if avg_ratings.get(book.id) is not None else None,
            "reviews_count": review_counts.get(book.id, 0),
        })

    return result


def create_review(session: Session, data: ReviewSchema, user_id: int):
    get_object(session, data.book_id, Book)

    if not data.summary.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"msg": "Sharh matni bo'sh bo'lishi mumkin emas"},
        )

    existing_review = (
        session.query(Review)
        .filter(Review.book_id == data.book_id, Review.user_id == user_id)
        .first()
    )
    if existing_review:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"msg": "Siz allaqachon ushbu kitob uchun sharh qoldirgansiz"},
        )

    review = Review(
        summary=data.summary.strip(),
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


def review_list(session: Session, book_id: int, limit: int = 20, offset: int = 0):
    get_object(session, book_id, Book)
    reviews = (
        session.query(Review)
        .filter(Review.book_id == book_id)
        .order_by(Review.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
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
    get_object(session, data.book_id, Book)

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

