from fastapi import APIRouter, Depends, status
from fastapi_jwt_auth2 import AuthJWT
from sqlalchemy.orm import Session
from db import get_db
from users.schema import SignUpSchema, LoginSchema, UserResponseSchema, ProfileUpdateSchema, ChangePasswordSchema
from users import auth

router = APIRouter()


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(new_user: SignUpSchema, db: Session = Depends(get_db)):
    return auth.register(new_user, db)


@router.post("/login")
def login(data: LoginSchema, db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    return auth.login(data, db, Authorize)


@router.get("/profile", response_model=UserResponseSchema)
def profile(Authorize: AuthJWT = Depends(), db: Session = Depends(get_db)):
    return auth.get_profile(Authorize, db)


@router.patch("/profile-update", response_model=UserResponseSchema)
def profile_update_router(data:ProfileUpdateSchema, Authorize:AuthJWT = Depends(), db: Session = Depends(get_db)):
    return auth.profile_update(Authorize, data, db)

@router.patch("/change-password")
def change_password_router(data:ChangePasswordSchema, Authorize:AuthJWT = Depends(), db: Session = Depends(get_db)):
    return auth.change_password(data, Authorize, db)

@router.get('/token-refresh')
def token_refresh_router(Authorize: AuthJWT = Depends(), db: Session = Depends(get_db)):
    return auth.token_refresh(Authorize, db)

@router.post('/logout')
def logout_router(Authorize: AuthJWT = Depends(), db: Session = Depends(get_db)):
    return auth.logout(Authorize, db)