from typing import Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from app.domain.entities.user import User
from app.infrastructure.db.models.user_model import UserModel
from app.schemas.register_schema import RegisterRequest
from app.domain.exceptions.auth_exception import AuthException


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def find_by_email(self, email: str) -> Optional[User]:
        try:
            stmt = select(UserModel).where(
                UserModel.email == email.lower().strip())
            result = await self.session.execute(stmt)
            user_model = result.scalar_one_or_none()

            if user_model:
                return self._model_to_entity(user_model)
            return None

        except Exception as e:
            raise AuthException(f"Error finding user by email: {str(e)}")

    async def find_user_for_login(self, email: str) -> Optional[User]:
        try:
            stmt = select(UserModel).where(
                UserModel.email == email.lower().strip(),
                UserModel.is_active == True
            )
            result = await self.session.execute(stmt)
            user_model = result.scalar_one_or_none()

            if user_model:
                return self._model_to_entity(user_model)
            return None

        except Exception as e:
            raise AuthException(f"Error finding user for login: {str(e)}")

    async def find_by_user_id(self, user_id: UUID) -> Optional[User]:
        try:
            stmt = select(UserModel).where(UserModel.user_id == user_id)
            result = await self.session.execute(stmt)
            user_model = result.scalar_one_or_none()

            if user_model:
                return self._model_to_entity(user_model)
            return None

        except Exception as e:
            raise AuthException(f"Error finding user by ID: {str(e)}")

    async def email_exists(self, email: str) -> bool:
        try:
            stmt = select(UserModel.user_id).where(
                UserModel.email == email.lower().strip())
            result = await self.session.execute(stmt)
            return result.scalar_one_or_none() is not None

        except Exception as e:
            raise AuthException(f"Error checking email existence: {str(e)}")

    async def create_user(self, user_data: dict) -> User:
        try:
            user_model = UserModel(
                email=user_data["email"],
                name=user_data["name"],
                password=user_data["password"],
                is_active=user_data.get("is_active", True),
                is_superuser=user_data.get("is_superuser", False),
                is_reset_password=user_data.get("is_reset_password", False)
            )
            self.session.add(user_model)
            await self.session.commit()
            await self.session.refresh(user_model)

            return self._model_to_entity(user_model)

        except IntegrityError as e:
            await self.session.rollback()
            if "unique constraint" in str(e).lower() and "email" in str(e).lower():
                raise AuthException("Email already exists")
            raise AuthException(f"Database integrity error: {str(e)}")
        except Exception as e:
            await self.session.rollback()
            raise AuthException(f"Error creating user: {str(e)}")

    async def create_new_user(self, register_data: RegisterRequest, processed_data: dict) -> User:
        if await self.email_exists(register_data.email):
            raise AuthException("Email already registered")

        return await self.create_user(processed_data)

    async def update_user(self, user_id: UUID, update_data: dict) -> User:
        try:
            stmt = select(UserModel).where(UserModel.user_id == user_id)
            result = await self.session.execute(stmt)
            user_model = result.scalar_one_or_none()

            if not user_model:
                raise AuthException("User not found")

            for field, value in update_data.items():
                if hasattr(user_model, field) and value is not None:
                    setattr(user_model, field, value)

            await self.session.commit()
            await self.session.refresh(user_model)

            return self._model_to_entity(user_model)

        except AuthException:
            raise
        except Exception as e:
            await self.session.rollback()
            raise AuthException(f"Error updating user: {str(e)}")

    async def delete_user(self, user_id: UUID) -> bool:
        try:
            stmt = select(UserModel).where(UserModel.user_id == user_id)
            result = await self.session.execute(stmt)
            user_model = result.scalar_one_or_none()

            if not user_model:
                return False

            user_model.is_active = False
            await self.session.commit()

            return True

        except Exception as e:
            await self.session.rollback()
            raise AuthException(f"Error deleting user: {str(e)}")

    async def activate_user(self, user_id: UUID) -> User:
        return await self.update_user(user_id, {"is_active": True})

    async def deactivate_user(self, user_id: UUID) -> User:
        return await self.update_user(user_id, {"is_active": False})

    def _model_to_entity(self, user_model: UserModel) -> User:
        return User(
            email=user_model.email,
            name=user_model.name,
            password=user_model.password,
            is_active=user_model.is_active,
            is_superuser=user_model.is_superuser,
            is_reset_password=user_model.is_reset_password
        )
