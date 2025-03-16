from datetime import datetime
from typing import Literal, Optional

from sqlmodel import Field, SQLModel, String


class Tasks(SQLModel, table=True):
    id: int = Field(primary_key=True)
    summary: str
    description: Optional[str] = Field(default=None)
    status: Literal["to_do", "in_progress", "done"] = Field(sa_type=String)
    created_at: datetime
    created_by: Optional[int] = Field(default=None, foreign_key="users.id")
    updated_at: Optional[datetime] = Field(default=None)
    updated_by: Optional[int] = Field(default=None, foreign_key="users.id")
    deleted_at: Optional[datetime] = Field(default=None)
    deleted_by: Optional[int] = Field(default=None, foreign_key="users.id")
