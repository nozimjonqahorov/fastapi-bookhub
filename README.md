# Bookhub API

A book catalog and review platform built with FastAPI. Users can browse books, write reviews, manage a wishlist, and read news. Admins manage authors, categories, books, and news articles.

## Tech Stack

- **FastAPI** — REST API framework
- **SQLAlchemy** — ORM
- **Alembic** — database migrations
- **PostgreSQL** — primary database
- **fastapi-jwt-auth2** — JWT authentication with refresh-token denylist
- **Pydantic** — request/response validation
- **Werkzeug** — password hashing

## Features

- User registration, login, profile management, and password change
- JWT access/refresh tokens with logout via token blacklist
- Role-based access control (`user` and `admin`)
- **Books:** CRUD for authors, categories, and books (admin); public listing with search and filters
- **Reviews:** Authenticated users can create, update, and delete their own reviews; admins can manage any review
- **Wishlist:** Toggle books in a personal wishlist (owner-only)
- **News:** Admin-managed news articles with public read access

## Project Structure

```
bookhub/
├── main.py              # FastAPI app entry point
├── db.py                # Database engine and session
├── permissions.py       # Auth dependencies (current user, admin)
├── requirements.txt
├── alembic.ini
├── alembic/
│
├── users/
│   ├── models.py        # User, UserRole, BlackListToken
│   ├── schema.py
│   ├── auth.py
│   └── router.py
│
├── book/
│   ├── models.py        # Author, Category, Book, Review, Wishlist
│   ├── schema.py
│   ├── crud.py
│   └── router.py
│
└── news/
    ├── models.py        # News
    ├── schema.py
    ├── crud.py
    └── router.py
```

## Prerequisites

- Python 3.11+
- PostgreSQL 14+

## Installation

1. **Clone the repository**

```bash
git clone <repo-url>
cd bookhub
```

2. **Create and activate a virtual environment**

```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # macOS / Linux
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Create a PostgreSQL database**

```sql
CREATE DATABASE bookhub_db;
```

5. **Configure environment variables**

Create a `.env` file in the project root:

```env
DATABASE_URL=postgresql+psycopg://user:password@localhost:5432/bookhub_db
AUTHJWT_SECRET_KEY=your-secret-key-here
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

| Variable | Required | Description |
|---|---|---|
| `DATABASE_URL` | Yes | PostgreSQL connection string |
| `AUTHJWT_SECRET_KEY` | Yes | Secret key for signing JWT tokens |
| `CORS_ORIGINS` | No | Comma-separated allowed origins (defaults to `*`) |

6. **Run database migrations**

```bash
alembic revision --autogenerate -m "initial migration"
alembic upgrade head
```

7. **Start the server**

```bash
uvicorn main:app --reload
```

API documentation (Swagger UI): [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

## Authentication

1. Register via `POST /auth/register` or log in via `POST /auth/login`.
2. Copy the `access` token from the response.
3. In Swagger UI, click **Authorize** and enter: `Bearer <your_access_token>`

Additional auth endpoints:

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/auth/profile` | Get current user profile |
| `PATCH` | `/auth/profile-update` | Update profile |
| `PATCH` | `/auth/change-password` | Change password |
| `GET` | `/auth/token-refresh` | Refresh access token |
| `POST` | `/auth/logout` | Logout (blacklist refresh token) |

## API Overview

### Auth — `/auth`

| Method | Endpoint | Access |
|---|---|---|
| `POST` | `/register` | Public |
| `POST` | `/login` | Public |
| `GET` | `/profile` | Authenticated |
| `PATCH` | `/profile-update` | Authenticated |
| `PATCH` | `/change-password` | Authenticated |
| `GET` | `/token-refresh` | Authenticated |
| `POST` | `/logout` | Authenticated |

### Books — `/books`

| Method | Endpoint | Access |
|---|---|---|
| `POST` | `/create-author` | Admin |
| `GET` | `/list-author/` | Public |
| `GET` | `/detail-author/{author_id}` | Public |
| `PATCH` | `/update-author/{author_id}` | Admin |
| `DELETE` | `/delete-author/{author_id}` | Admin |
| `POST` | `/create-category` | Admin |
| `GET` | `/list-category/` | Public |
| `GET` | `/detail-category/{category_id}` | Public |
| `PATCH` | `/update-category/{category_id}` | Admin |
| `DELETE` | `/delete-category/{category_id}` | Admin |
| `POST` | `/create-book` | Authenticated |
| `GET` | `/list-book/` | Public |
| `GET` | `/detail-book/{book_id}` | Public |
| `PATCH` | `/update-book/{book_id}` | Admin |
| `DELETE` | `/delete-book/{book_id}` | Admin |
| `POST` | `/create-review` | Authenticated |
| `PATCH` | `/update-review/{review_id}` | Owner or Admin |
| `GET` | `/book/reviews/list/{book_id}` | Public |
| `DELETE` | `/delete-review/{review_id}` | Owner or Admin |
| `POST` | `/wishlist/` | Authenticated |
| `GET` | `/wishlist/my` | Authenticated |

**Book list query parameters:** `title`, `author_id`, `category_id`, `ordering`, `limit`, `offset`

### News — `/news`

| Method | Endpoint | Access |
|---|---|---|
| `POST` | `/create-news` | Admin |
| `GET` | `/list-news/` | Public |
| `GET` | `/detail-news/{news_id}` | Public |
| `PATCH` | `/update-news/{news_id}` | Admin |
| `DELETE` | `/delete-news/{news_id}` | Admin |

## Database Migrations

When you change a model, generate and apply a new migration:

```bash
alembic revision --autogenerate -m "describe your change"
alembic upgrade head
```

## Response Format

All API responses follow a consistent structure:

```json
{
  "msg": "Success message or error detail",
  "status": 200,
  "data": {}
}
```

Validation errors return HTTP `422` with error details in the `data` field.

## License

This project is for educational purposes.
