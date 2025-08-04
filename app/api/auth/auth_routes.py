from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.login_schema import LoginRequest, LoginResponse
from app.schemas.register_schema import RegisterRequest, RegisterResponse
from app.domain.services.auth_service import auth_service
from app.domain.services.jwt_service import jwt_service
from app.infrastructure.db.repositories.user_repository import UserRepository
from app.api.dependencies.database import get_db_session
from app.api.dependencies.auth import get_current_user, get_current_active_user
from app.domain.exceptions.auth_exception import AuthException

router = APIRouter(prefix="/auth", tags=["Authentication"])

security = HTTPBearer()


@router.post("/login", response_model=LoginResponse)
async def login(
    login_data: LoginRequest,
    db: AsyncSession = Depends(get_db_session)
):
    try:
        user_repo = UserRepository(db)
        user = await auth_service.authenticate_user(
            email=login_data.email,
            password=login_data.password,
            user_repository=user_repo
        )

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        token_data = auth_service.validate_user_for_token(user)
        access_token = jwt_service.create_access_token(token_data)
        user_response_data = auth_service.sanitize_user_response(user)

        return LoginResponse(
            access_token=access_token,
            token_type="bearer",
            user=RegisterResponse(**user_response_data)
        )

    except AuthException as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during login"
        )


@router.post("/register", response_model=RegisterResponse)
async def register(
    register_data: RegisterRequest,
    db: AsyncSession = Depends(get_db_session)
):
    try:
        user_repo = UserRepository(db)
        processed_data = auth_service.prepare_user_for_registration(
            register_data)
        new_user = await user_repo.create_new_user(register_data, processed_data)
        user_response_data = auth_service.sanitize_user_response(new_user)
        return RegisterResponse(**user_response_data)
    except AuthException as e:
        if "already" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=str(e)
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during registration"
        )


@router.get("/me", response_model=RegisterResponse)
async def get_current_user_info(
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Get current user information based on JWT token
    """
    try:
        user_repo = UserRepository(db)
        user = await user_repo.find_by_email(current_user["email"])

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        user_response_data = auth_service.sanitize_user_response(user)
        return RegisterResponse(**user_response_data)

    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/validate-token")
def validate_token(
    current_user: dict = Depends(get_current_user)
):
    """
    Validate JWT token and return token information
    """
    try:
        return {
            "valid": True,
            "user": {
                "email": current_user["email"],
                "name": current_user["name"],
                "is_active": current_user["is_active"]
            }
        }

    except Exception:
        return {"valid": False, "message": "Token validation error"}
