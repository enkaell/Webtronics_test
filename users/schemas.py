from pydantic import BaseModel


class UserRegisterSchema(BaseModel):
    mail: str
