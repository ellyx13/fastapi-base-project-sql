from datetime import datetime
from typing import Literal, Optional
from typing_extensions import Self

from sqlmodel import Field, SQLModel, String
from . import schemas

class Tasks(SQLModel, table=True):
    id: int = Field(primary_key=True)
    summary: str
    description: Optional[str] = Field(default=None)
    status: Literal["to_do", "in_progress", "done"] = Field(sa_type=String)
    created_at: datetime = Field(default_factory=datetime.now)
    created_by: Optional[int] = Field(default=None, foreign_key="users.id")
    updated_at: Optional[datetime] = Field(default=None)
    updated_by: Optional[int] = Field(default=None, foreign_key="users.id")
    deleted_at: Optional[datetime] = Field(default=None)
    deleted_by: Optional[int] = Field(default=None, foreign_key="users.id")


    @classmethod
    def from_create_request(cls, data: schemas.CreateRequest, status: str = "to_do") -> Self:
        return cls(
            summary=data.summary,
            description=data.description,
            status=status
        )