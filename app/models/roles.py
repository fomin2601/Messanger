from sqlmodel import SQLModel, Field, Relationship
from typing import Optional


class UserRole(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    role_name: str = Field(nullable=False)
    user_link: Optional['UserRoleLink'] = Relationship(back_populates='role')
