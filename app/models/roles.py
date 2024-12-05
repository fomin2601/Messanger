from sqlmodel import SQLModel, Field
from typing import Optional


class UserRole(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    role_name: str = Field(nullable=False)
