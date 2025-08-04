from app.core.camel_case_config import CamelBaseModel
from pydantic import EmailStr, Field
from typing import Optional


class RegisterRequest(CamelBaseModel):
    email: EmailStr
    name: str = Field(..., min_length=2, max_length=100)
    password: str = Field(..., min_length=8, description="User password")


class RegisterResponse(CamelBaseModel):
    email: str
    name: str
    is_active: bool
    is_superuser: bool
    is_reset_password: bool


class UserUpdate(CamelBaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None
    is_reset_password: Optional[bool] = None
