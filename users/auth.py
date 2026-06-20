import re
from fastapi import status
from fastapi.exceptions import HTTPException                                           
from fastapi_jwt_auth2 import AuthJWT                                    
from sqlalchemy.orm import Session                                                
from werkzeug.security import generate_password_hash, check_password_hash
from .models import User, BlackListToken
from .schema import SignUpSchema, LoginSchema, ProfileUpdateSchema, ChangePasswordSchema
from fastapi_jwt_auth2.exceptions import AuthJWTException

def check_user(db: Session, column, value):
    user = db.query(User).filter(column == value).first()
    if user:
        raise HTTPException(status_code=400, detail=f'Bu {value} allaqachon mavjud')

def check_pass(password, conf_password=None):

    if not password or not conf_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={'msg': 'Parol va tasdiqlash maydoni to\'ldirilishi shart'}
        )
    
    regex = re.fullmatch(
        re.compile(r"^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$ %^&*-]).{8,}$"), 
        password
    )
    
    if not regex:
        raise HTTPException(status_code=400, detail='Parol kuchsiz')
    
    if password and conf_password and password != conf_password:
        raise HTTPException(status_code=400, detail='Parollar mos emas')
        
    return True


def register(new_user: SignUpSchema, db: Session):
    check_user(db, User.username, new_user.username)
    check_user(db, User.email, new_user.email)
    check_user(db, User.phone_number, new_user.phone_number)
    check_pass(new_user.password, new_user.conf_password)

    user = User(
        first_name = new_user.first_name,
        last_name = new_user.last_name,
        username = new_user.username,
        email = new_user.email,
        phone_number = new_user.phone_number,
        password = generate_password_hash(new_user.password)  
    )
    

    db.add(user)
    db.commit()
    db.refresh(user)
    
    return {
        "msg": 'Register',
        'status': status.HTTP_201_CREATED
    }


def login(data: LoginSchema, db: Session, Authorize: AuthJWT):
    db_user = db.query(User).filter(User.username == data.username).first()
    if not db_user:
        raise HTTPException(status_code=400, detail='Bu username majud emas')

    if not check_password_hash(db_user.password, data.password):
        raise HTTPException(status_code=400, detail='Parol xato')

    refresh_token = Authorize.create_refresh_token(subject=str(db_user.id))
    access_token = Authorize.create_access_token(subject=str(db_user.id))

    return {
        "msg": 'login',
        'access': access_token.decode() if isinstance(access_token, bytes) else access_token,
        'refresh': refresh_token.decode() if isinstance(refresh_token, bytes) else refresh_token,
    }


def get_profile(Authorize: AuthJWT, db: Session):
    try:
        Authorize.jwt_required()  
    except AuthJWTException as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"msg": e.message}
        ) 
    current_user_id = Authorize.get_jwt_subject()
    
    user = db.query(User).filter(User.id == int(current_user_id)).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"msg": "Foydalanuvchi topilmadi"}
        )
    return user

def profile_update(Authorize:AuthJWT, data : ProfileUpdateSchema, db : Session):
    try:
        Authorize.jwt_required()  
    except AuthJWTException as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"msg": e.message}
        ) 
    user_id = Authorize.get_jwt_subject()
    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"msg": "Foydalanuvchi topilmadi"}
        )
    
    for i, j in data.model_dump(exclude_unset=True).items():
        setattr(user, i, j)

    db.commit()
    db.refresh(user)

    return user


def change_password(data : ChangePasswordSchema, Authorize : AuthJWT, db: Session):
    try:
        Authorize.jwt_required()  
    except AuthJWTException as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"msg": e.message}
        ) 
    
    user_id = Authorize.get_jwt_subject()
    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"msg": "Foydalanuvchi topilmadi"}
        )
    old_passwod = data.old_password

    if old_passwod == data.new_password:
        raise HTTPException(detail="Yangi parol va eski parol bir xil bo'lishi mumkin emas", status_code=400)
    
    if not check_password_hash(user.password, old_passwod):
        raise HTTPException(detail="Eski parol xato!", status_code=400)
    
    check_pass(data.new_password, data.confirm_password)

    user.password = generate_password_hash(data.new_password)
    db.commit()
    db.refresh(user)

    return {"msg":"Password changed", "status":status.HTTP_200_OK}
        

def token_refresh(Authorize: AuthJWT, db: Session):
    try:
        Authorize.jwt_refresh_token_required()
        user_id = Authorize.get_jwt_subject()
        access = Authorize.create_access_token(subject=str(user_id))
        return {
            'msg': 'new access token',
            'access_token': access
        }
        
    except:
        raise HTTPException(detail='Token error', status_code=status.HTTP_400_BAD_REQUEST)
    


def logout(Authorize: AuthJWT, db: Session):
    try:
        Authorize.jwt_refresh_token_required()
        
    except:
        raise HTTPException(detail={
            'msg': f'Token error',
            'status': status.HTTP_400_BAD_REQUEST
        }, status_code=status.HTTP_400_BAD_REQUEST)
        
    else:
        jti = Authorize.get_raw_jwt()['jti']
        token = BlackListToken(jti=jti)
        
        db.add(token)
        db.commit()
        db.refresh(token)
        
        return {
            'msg': 'Logout',
        }