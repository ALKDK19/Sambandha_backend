from datetime import datetime
from typing import Optional

from pydantic import EmailStr, BaseModel

from app.schemas.base import BaseSchema


class UserBase(BaseSchema):
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    auth_provider: Optional[str] = None
    preferred_language: Optional[str] = "en_US"
    theme_preference: Optional[str] = "light"


class UserCreate(UserBase):
    password: str


class UserUpdate(UserBase):
    password: Optional[str] = None


class UserInDB(UserBase):
    user_id: int
    is_phone_verified: bool = False
    is_email_verified: bool = False
    account_status: str = "active"
    created_at: datetime
    updated_at: datetime


class UserLogin(BaseModel):
    email_or_phone: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user_id: Optional[int] = None
