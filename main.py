from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from fastapi_jwt_auth2 import AuthJWT

from book.router import router as book_router
from users.router import router as auth_router
from users.schema import Settings
from db import Base, engine
import users.models

Base.metadata.create_all(bind=engine)

app = FastAPI(
    swagger_ui_parameters={"syntaxHighlight.theme": "obsidian"}
)

@AuthJWT.load_config
def get_config():
    return Settings()

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="Book Shop API",
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

app.include_router(auth_router, prefix="/auth")
app.include_router(book_router, prefix="/books")