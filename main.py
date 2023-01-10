import uvicorn

from fastapi import FastAPI, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from db_init import connect_db, get_session
from users.utils import validate_register_data
from users.schemas import UserRegisterSchema

app = FastAPI()
connect_db()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')


@app.get("/")
def root():
    return {"message": "Hello from user's app!"}


@app.post("/register")
def register(user: UserRegisterSchema = Depends(), db: Session = Depends(get_session),
             form_data: OAuth2PasswordRequestForm = Depends()):
    validate_register_data(user, db, form_data)
    return {"token": "vlad"}


if __name__ == "__main__":
    uvicorn.run(app)
