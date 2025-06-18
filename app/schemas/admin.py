from typing import Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime

from app.schemas.base import BaseSchema

class AdminBase(BaseSchema):
    username: str
    email: EmailStr
    full_name: str
    role: str = "admin"

class AdminCreate(AdminBase):
    password: str

class AdminUpdate(AdminBase):
    password: Optional[str] = None

class AdminInDB(AdminBase):
    admin_id: int
    is_active: bool = True
    last_login: Optional[datetime] = None
    created_at: datetime

class AdminLogin(BaseModel):
    username: str
    password: str

class AdminToken(BaseModel):
    access_token: str
    token_type: str