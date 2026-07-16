import os
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi_jwt_auth2 import AuthJWT

from book.router import router as book_router
from users.router import router as auth_router
from news.router import router as news_router


from users.schema import Settings
from users.models import BlackListToken
from db import Base, engine, SessionLocal
import users.models

app = FastAPI(
    swagger_ui_parameters={"syntaxHighlight.theme": "obsidian"}
)

allowed_origins = [origin.strip() for origin in os.getenv("CORS_ORIGINS", "*").split(",") if origin.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins or ["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


@app.exception_handler(HTTPException)
def http_exception_handler(request: Request, exc: HTTPException):
    detail = exc.detail
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "msg": detail if isinstance(detail, str) else detail,
            "status": exc.status_code,
            "data": None,
        },
    )


@app.exception_handler(RequestValidationError)
def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "msg": "Validation failed",
            "status": 422,
            "data": exc.errors(),
        },
    )


@app.exception_handler(Exception)
def generic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "msg": "Server error",
            "status": 500,
            "data": str(exc),
        },
    )


@AuthJWT.load_config
def get_config():
    return Settings()


@AuthJWT.token_in_denylist_loader
def check_if_token_in_denylist(decrypted_token):
    jti = decrypted_token['jti']
    session = SessionLocal()
    try:
        token = session.query(BlackListToken).filter(BlackListToken.jti == jti).first()
        return token is not None
    finally:
        session.close()


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="Bookhub API",
        version="1.0.0",
        description="JWT Autentifikatsiya bilan himoyalangan API",
        routes=app.routes,
    )

    openapi_schema["components"]["securitySchemes"] = {
        "AuthJWT": {
            "type": "apiKey",
            "in": "header",
            "name": "Authorization",
            "description": "Tokenni quyidagi ko'rinishda kiriting: Bearer <Sizning_Tokeningiz>"
        }
    }

    openapi_schema["security"] = [{"AuthJWT": []}]

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi

app.include_router(auth_router, prefix="/auth", tags=["Auth"])
app.include_router(book_router, prefix="/books", tags=["Books"])
app.include_router(news_router, prefix="/news", tags=["News"])