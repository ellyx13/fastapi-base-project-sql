from typing import Optional

from core.schemas import EmailStr, PhoneStr
from pydantic import BaseModel, field_validator, ConfigDict
from users import schemas as user_schemas
from users.config import settings as user_settings
from users.exceptions import UserErrorCode


class RegisterRequest(BaseModel):
    fullname: str
    email: EmailStr
    phone_number: Optional[PhoneStr] = None
    password: str

    @field_validator("password")
    @classmethod
    def check_the_minimum_length_of_the_password(cls, v: str) -> str:
        if len(v) < user_settings.minimum_length_of_the_password:
            raise UserErrorCode.InvalidPasswordLength()
        return v


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(user_schemas.Response):
    access_token: str
    token_type: str = "bearer"
