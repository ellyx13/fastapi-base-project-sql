from datetime import datetime
from typing import Literal, Optional

from core.schemas import EmailStr, ObjectIdStr, PhoneStr
from sqlmodel import Field, SQLModel, String


class Users(SQLModel, table=True):
    id: int = Field(primary_key=True)
    fullname: str
    email: EmailStr = Field(index=True, unique=True)
    phone_number: Optional[PhoneStr] = Field(default=None)
    password: bytes
    type: Literal["admin", "user"] = Field(sa_type=String)
    created_at: datetime
    created_by: Optional[int] = Field(default=None, foreign_key="users.id")
    updated_at: Optional[datetime] = Field(default=None)
    updated_by: Optional[int] = Field(default=None, foreign_key="users.id")
    deleted_at: Optional[datetime] = Field(default=None)
    deleted_by: Optional[int] = Field(default=None, foreign_key="users.id")