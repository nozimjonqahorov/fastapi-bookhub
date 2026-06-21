# Bookshop API

Kitob katalogi va sharh/reyting platformasi — FastAPI asosida qurilgan REST API.

## Texnologiyalar

- FastAPI
- SQLAlchemy (ORM) + Alembic (migratsiya)
- SQLite
- fastapi-jwt-auth2 (JWT autentifikatsiya, refresh token denylist)
- Pydantic
- Werkzeug (parol hash)

## O'rnatish va ishga tushirish

```bash
git clone <repo-url>
cd <repo-nomi>

python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux

pip install -r requirements.txt

uvicorn main:app --reload
```

Swagger UI: http://127.0.0.1:8000/docs

**Eslatma:** `bookshop.db` fayli repoda allaqachon namuna ma'lumotlar bilan
to'ldirilgan holda mavjud. Alohida migratsiya yoki seed skript ishlatish
SHART EMAS — serverni ishga tushirgandan so'ng darhol pastdagi login
ma'lumotlari bilan sinab ko'rishingiz mumkin.

## Test uchun tayyor login ma'lumotlari

### Adminlar (kitob/muallif/kategoriya yaratish huquqiga ega)

| Username | Parol |
|---|---|
| `admin1` | `Admin123!` |
| `admin2` | `Admin456!` |

### Oddiy foydalanuvchilar (sharh yozish, wishlist'ga qo'shish huquqiga ega)

| Username | Parol |
|---|---|
| `ali_99` | `Ali1234!` |
| `dilnoza21` | `Dilnoza1!` |
| `javohir07` | `Javohir1!` |
| `malika_b` | `Malika1!` |

Login qilish: `POST /auth/login` — javobda kelgan `access` tokenini
Swagger UI'dagi "Authorize" tugmasi orqali `Bearer <token>` ko'rinishida kiriting.

## Asosiy funksionallik

- Ro'yxatdan o'tish, login, JWT autentifikatsiya, logout (refresh token blacklist)
- Admin: muallif, kategoriya, kitob va yangilik (news) yaratish/tahrirlash/o'chirish
- Hamma: kitoblarni ko'rish, qidirish (sarlavha bo'yicha), filtrlash (muallif/kategoriya bo'yicha)
- Login qilingan foydalanuvchi: sharh (review) yozish, reyting qo'yish, wishlist'ga
  kitob qo'shish/olib tashlash
- Sharhni faqat egasi yoki admin o'chira/tahrirlay oladi
- Wishlist obyektini faqat egasi boshqara oladi (admin ham aralashmaydi)

## Loyiha tuzilishi

```
book_shop/
├── main.py
├── db.py
├── permissions.py
├── requirements.txt
├── alembic.ini
├── alembic/
├── bookshop.db
│
├── users/
│   ├── models.py      (User, UserRole, BlackListToken)
│   ├── schema.py
│   ├── auth.py
│   └── router.py
│
├── book/
│   ├── models.py       (Author, Category, Book, Review, Wishlist)
│   ├── schema.py
│   ├── crud.py
│   └── router.py
│
└── news/
    ├── models.py        (News)
    ├── schema.py
    ├── crud.py
    └── router.py
```

## Ma'lumotlar bazasi

SQLite ishlatiladi. Jadval tuzilishi Alembic migratsiyalari orqali
boshqariladi (`alembic/versions/`). Model o'zgartirilganda:

```bash
alembic revision --autogenerate -m "tavsif"
alembic upgrade head
```
