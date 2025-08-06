from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional

from app.domain.services.jwt_service import jwt_service
from app.domain.exceptions.auth_exception import InvalidTokenException


security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    try:
        token = credentials.credentials
        payload = jwt_service.decode_access_token(token)
        email: str = payload.get("email")
        if email is None:
            raise InvalidTokenException()

        return {
            "email": email,
            "name": payload.get("name", ""),
            "is_active": payload.get("is_active", True),
            "is_superuser": payload.get("is_superuser", False),
            "is_reset_password": payload.get("is_reset_password", False)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e


def get_current_active_user(
    current_user: dict = Depends(get_current_user)
) -> dict:
    if not current_user.get("is_active"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user


def get_current_superuser(
    current_user: dict = Depends(get_current_user)
) -> dict:
    if not current_user.get("is_superuser"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user


def optional_auth(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(
        HTTPBearer(auto_error=False))
) -> Optional[dict]:
    if credentials is None:
        return None

    try:
        token = credentials.credentials
        payload = jwt_service.decode_access_token(token)
        return {
            "email": payload.get("email"),
            "name": payload.get("name", ""),
            "is_active": payload.get("is_active", True),
            "is_superuser": payload.get("is_superuser", False),
            "is_reset_password": payload.get("is_reset_password", False)
        }
    except Exception:
        return None
