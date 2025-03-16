from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, Field


class CreateRequest(BaseModel):
    summary: str
    description: Optional[str] = None


class Response(BaseModel):
    id: int
    summary: str
    description: Optional[str] = None
    status: str
    created_at: datetime
    created_by: int


class ListResponse(BaseModel):
    total_items: int
    total_page: int
    records_per_page: int
    results: List[Response]


class EditRequest(BaseModel):
    summary: Optional[str] = None
    description: Optional[str] = None
    status: Optional[Literal["to_do", "in_progress", "done"]] = None
