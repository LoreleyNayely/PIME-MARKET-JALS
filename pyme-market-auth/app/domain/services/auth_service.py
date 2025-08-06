from typing import Optional
from passlib.context import CryptContext
from app.domain.entities.user import User
from app.schemas.register_schema import RegisterRequest
from app.domain.exceptions.auth_exception import AuthException


class AuthService:
    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def hash_password(self, password: str) -> str:
        return self.pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return self.pwd_context.verify(plain_password, hashed_password)

    def validate_password_strength(self, password: str) -> None:
        if len(password) < 8:
            raise AuthException("Password must be at least 8 characters long")

        if not any(c.isupper() for c in password):
            raise AuthException(
                "Password must contain at least one uppercase letter")

        if not any(c.islower() for c in password):
            raise AuthException(
                "Password must contain at least one lowercase letter")

        if not any(c.isdigit() for c in password):
            raise AuthException("Password must contain at least one number")

    async def authenticate_user(self, email: str, password: str, user_repository) -> Optional[User]:
        user = await user_repository.find_user_for_login(email)
        if not user:
            return None
        if not user.is_active:
            raise AuthException("User account is inactive")
        if not self.verify_password(password, user.password):
            return None

        return user

    def prepare_user_for_registration(self, register_data: RegisterRequest) -> dict:
        self.validate_password_strength(register_data.password)
        hashed_password = self.hash_password(register_data.password)
        return {
            "email": register_data.email.lower().strip(),
            "name": register_data.name.strip(),
            "password": hashed_password,
            "is_active": True,
            "is_superuser": False,
            "is_reset_password": False
        }

    def validate_user_for_token(self, user: User) -> dict:
        if not user.is_active:
            raise AuthException("Cannot create token for inactive user")
        return {
            "email": user.email,
            "name": user.name,
            "is_superuser": user.is_superuser,
            "is_active": user.is_active
        }

    def sanitize_user_response(self, user: User) -> dict:
        return {
            "email": user.email,
            "name": user.name,
            "is_active": user.is_active,
            "is_superuser": user.is_superuser,
            "is_reset_password": user.is_reset_password
        }


auth_service = AuthService()
