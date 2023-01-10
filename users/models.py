from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from posts.models import Post
from db_init import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    mail = Column(String, unique=True, index=True)
    password_hash = Column(String)
    post = relationship("Post")
