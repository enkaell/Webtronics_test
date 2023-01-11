from sqlalchemy.orm import Session
from sqlalchemy import or_
from fastapi import HTTPException, status
import requests
from users.models import User
from jose import jwt
from datetime import datetime, timedelta
from passlib.context import CryptContext


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_user_id_by_username(username: str, db: Session):
    return True if db.query(User).filter_by(username=username).one_or_none().id else False


def validate_password(plain_password, hashed_password):
    if not pwd_context.verify(plain_password, hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect username or password")


def get_password_hash(password):
    return pwd_context.hash(password)


def validate_register_data(user, db: Session, form_data: dict):
    if db.query(User).filter(or_(User.username == form_data.username, User.mail == user.mail)).one_or_none():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists")
    response = requests.get('https://hunter.io/v2/email-count', params={'domain': user.mail, 'format': 'json'})
    if response.json().get('data')['total'] == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="E-mail not found")
    db.add(User(username=form_data.username, password_hash=get_password_hash(form_data.password), mail=user.mail))
    db.commit()


def create_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=1400)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, "PrettyFlowSecretKey", algorithm="HS256")
    return encoded_jwt


def login_user(db: Session, form_data: dict):
    if user := db.query(User).filter(User.username == form_data.username).one_or_none():
        validate_password(form_data.password, user.password_hash)
        user.token = create_token(data={'sub': user.username})
        db.add(user)
        db.commit()
        return user.token
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")