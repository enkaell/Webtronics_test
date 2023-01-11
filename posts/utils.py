from sqlalchemy.orm import Session
from sqlalchemy import  and_
from fastapi import HTTPException, status

from posts.models import Post
from posts.schemas import PostCreationSchema


def create_new_post(user_id: int, db: Session, post: PostCreationSchema):
    # posts with same title?
    new_row = Post(title=post.title, text=post.text, user_id=user_id)
    db.add(new_row)
    db.commit()
    return "Created successfully"


def edit_own_post(post_id: int, db: Session, post: PostCreationSchema):
    if post_row := db.query(Post).filter(Post.id == post_id).one_or_none():
        post_row.title = post.title
        post_row.text = post.text
        db.add(post_row)
        db.commit()
        return "Edited successfully"
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")


def get_all_posts(db: Session):
    # username instead of user_id ?
    return db.query(Post).all()


def get_one_post(post_id: int, db: Session):
    if post := db.query(Post).filter(Post.id == post_id).one_or_none():
        return post
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")


def set_mark_post(post_id: int, is_like: bool, db: Session, user_id: int):
    if post := db.query(Post).filter(Post.id == post_id).one_or_none():
        if post.user_id == user_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You can't mark your own posts")
        if is_like:
            post.likes = int(post.likes or 0) + 1
        else:
            post.dislikes = int(post.likes or 0) + 1
        db.add(post)
        db.commit()
        return "Marked successfully"
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")


def delete_one_post(post_id: int, db: Session, user_id: int):
    if db.query(Post).filter(and_(Post.id == post_id, Post.user_id == user_id)).one_or_none():
        db.query(Post).filter(Post.id == post_id).delete()
        db.commit()
        return "Deleted successfully"
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
