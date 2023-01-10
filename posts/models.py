from sqlalchemy import Column, ForeignKey, Integer, String

from db_init import Base


class Post(Base):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    text = Column(String)
    likes = Column(Integer)
    dislikes = Column(Integer)
    user_id = Column(Integer, ForeignKey("users.id"))
