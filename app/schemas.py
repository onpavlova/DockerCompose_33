from pydantic import BaseModel, EmailStr
from typing import List, Optional


class PostBase(BaseModel):
    title: str
    body: str


class PostCreate(PostBase):
    user_id: int


class Post(PostBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True


class UserBase(BaseModel):
    name: str
    username: str
    email: EmailStr


class UserCreate(UserBase):
    pass


class User(UserBase):
    id: int
    posts: List[Post] = []

    class Config:
        from_attributes = True