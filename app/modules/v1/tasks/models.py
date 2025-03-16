from datetime import datetime
from typing import Literal, Optional

from core.schemas import ObjectIdStr
from sqlmodel import Field, SQLModel


class Tasks(SQLModel, table=True):
    id: int = Field(primary_key=True)
    summary: str
    description: Optional[str] = Field(default=None)
    status: Literal["to_do", "in_progress", "done"]
    created_at: datetime
    created_by: Optional[ObjectIdStr] = Field(default=None, foreign_key="users.id")
    updated_at: Optional[datetime] = Field(default=None)
    updated_by: Optional[ObjectIdStr] = Field(default=None, foreign_key="users.id")
    deleted_at: Optional[datetime] = Field(default=None)
    deleted_by: Optional[ObjectIdStr] = Field(default=None, foreign_key="users.id")
