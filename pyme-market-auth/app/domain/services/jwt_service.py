from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from app.core.security_config import SecurityConfig
from app.domain.exceptions.auth_exception import AuthException


class JWTService:
    def __init__(self):
        self.secret_key = SecurityConfig.JWT_SECRET_KEY
        self.algorithm = SecurityConfig.JWT_ALGORITHM
        self.access_token_expire_minutes = SecurityConfig.JWT_ACCESS_TOKEN_EXPIRE_MINUTES

    def create_access_token(self, user_data: Dict[str, Any]) -> str:
        try:
            payload = user_data.copy()
            expire = datetime.now(
                timezone.utc) + timedelta(minutes=self.access_token_expire_minutes)
            payload.update({
                "exp": expire,
                "iat": datetime.now(timezone.utc),
                "type": "access"
            })
            token = jwt.encode(payload, self.secret_key,
                               algorithm=self.algorithm)
            return token

        except Exception as e:
            raise AuthException(f"Failed to create access token: {str(e)}")

    def decode_access_token(self, token: str) -> Dict[str, Any]:
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm]
            )
            if payload.get("type") != "access":
                raise AuthException("Invalid token type")
            return payload

        except JWTError as e:
            if "expired" in str(e).lower():
                raise AuthException("Token has expired")
            elif "signature" in str(e).lower():
                raise AuthException("Invalid token signature")
            else:
                raise AuthException(f"Invalid token: {str(e)}")
        except Exception as e:
            raise AuthException(f"Token decode error: {str(e)}")

    def validate_token(self, token: str) -> bool:
        try:
            self.decode_access_token(token)
            return True
        except AuthException:
            return False

    def extract_user_email_from_token(self, token: str) -> str:
        payload = self.decode_access_token(token)
        email = payload.get("email")
        if not email:
            raise AuthException("Email not found in token")
        return email

    def extract_user_data_from_token(self, token: str) -> Dict[str, Any]:
        payload = self.decode_access_token(token)
        user_data = {
            "email": payload.get("email"),
            "name": payload.get("name"),
            "is_superuser": payload.get("is_superuser", False),
            "is_active": payload.get("is_active", True)
        }
        if not user_data["email"]:
            raise AuthException("Invalid token: missing email")

        return user_data

    def get_token_expiration(self, token: str) -> datetime:
        payload = self.decode_access_token(token)
        exp_timestamp = payload.get("exp")
        if not exp_timestamp:
            raise AuthException("No expiration found in token")
        return datetime.fromtimestamp(exp_timestamp)

    def is_token_expired(self, token: str) -> bool:
        try:
            expiration = self.get_token_expiration(token)
            return datetime.now(timezone.utc) > expiration
        except AuthException:
            return True

    def refresh_token_if_needed(self, token: str, user_data: Dict[str, Any],
                                refresh_threshold_minutes: int = 15) -> Optional[str]:
        try:
            expiration = self.get_token_expiration(token)
            time_until_expiration = expiration - datetime.now(timezone.utc)
            if time_until_expiration.total_seconds() / 60 <= refresh_threshold_minutes:
                return self.create_access_token(user_data)
            return None
        except AuthException:
            return self.create_access_token(user_data)


jwt_service = JWTService()
