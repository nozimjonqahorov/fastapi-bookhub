from fastapi import Depends, HTTPException, status
from fastapi_jwt_auth2 import AuthJWT
from fastapi_jwt_auth2.exceptions import AuthJWTException
from sqlalchemy.orm import Session

from db import get_db
from users.models import User, UserRole


def get_current_user(Authorize: AuthJWT = Depends(), db: Session = Depends(get_db),) -> User:
    try:
        Authorize.jwt_required()
    except AuthJWTException as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e.message,
        )

    user_id = Authorize.get_jwt_subject()
    user = db.query(User).filter(User.id == int(user_id)).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Foydalanuvchi topilmadi",
        )
    return user


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bu amal uchun admin huquqi kerak",
        )
    return current_user

