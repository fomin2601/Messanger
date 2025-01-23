from pydantic import BaseModel, Field
from typing import Optional, List

from app.models.roles import UserRole


class UserRegistrationScheme(BaseModel):
    username: str
    hashed_password: str
    first_name: str
    second_name: str
    patronymic: Optional[str]
    roles: List[int]
    description: Optional[str]


class UserPublicScheme(BaseModel):
    id: int
    username: str
    first_name: str
    second_name: str
    patronymic: Optional[str]
    roles: Optional[List[UserRole]]
    is_active: bool
    description: Optional[str]


class UserUpdateScheme(BaseModel):
    username: Optional[str]
    first_name: Optional[str]
    second_name: Optional[str]
    patronymic: Optional[str]
    roles: Optional[List[int]]
    description: Optional[str]


class UserLoginScheme(BaseModel):
    username: str
    hashed_password: str
