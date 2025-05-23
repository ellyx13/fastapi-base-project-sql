from datetime import datetime
from typing import List, Optional

from core.schemas import EmailStr, PhoneStr
from pydantic import BaseModel, ConfigDict


class Response(BaseModel):
    id: int
    fullname: str
    email: EmailStr
    phone_number: Optional[PhoneStr] = None
    type: str
    created_at: datetime


class ListResponse(BaseModel):
    total_items: int
    total_page: int
    records_per_page: int
    results: List[Response]


class LoginResponse(Response):
    access_token: str
    token_type: str


class EditRequest(BaseModel):
    model_config = ConfigDict(extra="allow")
    fullname: Optional[str] = None
    phone_number: Optional[PhoneStr] = None
