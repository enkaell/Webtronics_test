import uvicorn

from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from jose import jwt, JWTError
from db_init import connect_db, get_session
from users.utils import validate_register_data, login_user, get_user_id_by_username
from users.schemas import UserRegisterSchema

from posts.schemas import PostCreationSchema
from posts.utils import create_new_post, edit_own_post, get_all_posts, get_one_post, set_mark_post

app = FastAPI()
connect_db()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_session)):
    try:
        payload = jwt.decode(token, "PrettyFlowSecretKey", algorithms="HS256")
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authorized")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authorized")
    if user_id := get_user_id_by_username(username, db):
        return user_id
    else:
        HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authorized")


@app.get("/")
def root():
    return {"message": "Hello from user's app!"}


@app.post("/register")
def register(user: UserRegisterSchema = Depends(), db: Session = Depends(get_session),
             form_data: OAuth2PasswordRequestForm = Depends()):
    validate_register_data(user, db, form_data)
    return {"message": "Register successfully"}


@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_session)):
    token = login_user(db, form_data)
    return {'access_token': token, 'token_type': 'bearer'}


@app.get("/posts")
def get_posts(db: Session = Depends(get_session)):
    return get_all_posts(db)


@app.get("/posts/{post_id}")
def get_post(post_id: int, db: Session = Depends(get_session)):
    return get_one_post(post_id, db)


@app.get("/posts/{post_id}/is_like")
def like_post(is_like: bool, post_id: int, db: Session = Depends(get_session), user_id=Depends(get_current_user)):
    return set_mark_post(post_id, is_like, db, user_id)


@app.post("/posts/create")
def create_post(user_id: int = Depends(get_current_user), db: Session = Depends(get_session),
                post: PostCreationSchema = Depends()):
    return {"message": create_new_post(user_id, db, post)}


@app.put("/posts/{post_id}")
def edit_post(post_id: int, db: Session = Depends(get_session), post: PostCreationSchema = Depends(),
              user_id=Depends(get_current_user)):
    return {"message": edit_own_post(post_id, db, post)}


if __name__ == "__main__":
    uvicorn.run(app)
