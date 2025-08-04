from app.core.camel_case_config import CamelBaseModel
from pydantic import EmailStr, Field
from app.schemas.register_schema import RegisterResponse


class LoginRequest(CamelBaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, description="User password")


class LoginResponse(CamelBaseModel):
    access_token: str
    user: RegisterResponse
