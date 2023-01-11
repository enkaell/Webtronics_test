from pydantic import BaseModel


class PostCreationSchema(BaseModel):
    title: str
    text: str
