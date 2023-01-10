from sqlalchemy.orm import Session
from sqlalchemy import or_
from fastapi import HTTPException, status
import requests
from users.models import User


def validate_register_data(user, db: Session, form_data: dict):
    if db.query(User).filter(or_(User.username == form_data.username, User.mail == user.mail)).one_or_none():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists")
    response = requests.get('https://hunter.io/v2/email-count', params={'domain': user.mail, 'format': 'json'})
    if response.json().get('data')['total'] == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="E-mail not found")
    db.add(User(username=form_data.username, password_hash=form_data.password, mail=user.mail))
    db.commit()
