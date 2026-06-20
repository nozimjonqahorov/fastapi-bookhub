from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import timedelta

class SignUpSchema(BaseModel):
    first_name: str
    last_name: Optional[str] = None
    username: str
    email: EmailStr
    phone_number: str
    password: str
    conf_password: str

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "first_name": "Ali",
                "last_name": "Valiyev",
                "username": "ali123",
                "email": "ali@example.com",
                "phone_number": "+998901234567",
                "password": "StrongPass123!",
                "conf_password": "StrongPass123!"
            }
        }
    }


class UserResponseSchema(BaseModel):
    id: int
    first_name: str
    last_name: Optional[str] = None
    username: str
    email: EmailStr
    phone_number: str
    password : str

    model_config = {
        "from_attributes": True
    }


class LoginSchema(BaseModel):
    username :str
    password : str

    model_config = {
        "from_attributes": True
    }

class Settings(BaseModel):
    authjwt_secret_key : str = "5ca41016b054e7108c240380ef69e38c05a3e415dffd13a2a2078ef6410f4ef2"
    authjwt_access_token_expires : timedelta = timedelta(minutes=40)
    authjwt_refresh_token_expires : timedelta = timedelta(days=1)

class ProfileUpdateSchema(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    username: Optional[str] = None
    email: Optional[str] = None
    phone_number: Optional[str] = None
    
    model_config = {
        "from_attributes": True
    }

class ChangePasswordSchema(BaseModel):
    old_password : str
    new_password : str
    confirm_password : str

    model_config = {
        "from_attributes": True
    }