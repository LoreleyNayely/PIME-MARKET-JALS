from typing import Optional, List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.exc import IntegrityError
from app.domain.entities.cart import Cart
from app.infrastructure.db.models.cart_model import CartModel
from app.schemas.cart_schema import CartCreate, CartUpdate
from app.domain.exceptions.not_found_exception import NotFoundException
from app.domain.exceptions.internal_exception import InternalException


class CartRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_cart(self, cart_data: CartCreate) -> Cart:
        """Crear un nuevo carrito"""
        try:
            cart_model = CartModel(
                user_id=cart_data.user_id,
                status=cart_data.status,
                total_amount=0.00,
                total_items=0,
                is_active=True
            )

            self.session.add(cart_model)
            await self.session.commit()
            await self.session.refresh(cart_model)

            return self._model_to_entity(cart_model)

        except IntegrityError as e:
            await self.session.rollback()
            error_details = str(e.orig) if hasattr(e, 'orig') else str(e)
            raise Exception(
                f"Database integrity error when creating cart: {error_details}") from e
        except Exception as e:
            await self.session.rollback()
            raise Exception(
                f"Database error when creating cart: {type(e).__name__}: {str(e)}") from e

    async def get_cart_by_id(self, cart_id: UUID) -> Optional[Cart]:
        """Obtener carrito por ID"""
        try:
            stmt = select(CartModel).where(CartModel.cart_id == cart_id)
            result = await self.session.execute(stmt)
            cart_model = result.scalar_one_or_none()

            if cart_model:
                return self._model_to_entity(cart_model)
            return None

        except Exception as e:
            raise InternalException() from e

    async def get_active_cart_by_user(self, user_id: str) -> Optional[Cart]:
        """Obtener carrito activo de un usuario"""
        try:
            stmt = select(CartModel).where(
                and_(
                    CartModel.user_id == user_id,
                    CartModel.status == "active",
                    CartModel.is_active == True
                )
            ).order_by(CartModel.created_at.desc())

            result = await self.session.execute(stmt)
            cart_model = result.scalar_one_or_none()

            if cart_model:
                return self._model_to_entity(cart_model)
            return None

        except Exception as e:
            error_msg = f"Error getting active cart for user {user_id}: {type(e).__name__}: {str(e)}"
            raise Exception(error_msg) from e

    async def get_carts_by_user(self, user_id: str, include_inactive: bool = False) -> List[Cart]:
        """Obtener todos los carritos de un usuario"""
        try:
            if include_inactive:
                stmt = select(CartModel).where(
                    CartModel.user_id == user_id
                ).order_by(CartModel.created_at.desc())
            else:
                stmt = select(CartModel).where(
                    and_(
                        CartModel.user_id == user_id,
                        CartModel.is_active == True
                    )
                ).order_by(CartModel.created_at.desc())

            result = await self.session.execute(stmt)
            cart_models = result.scalars().all()

            return [self._model_to_entity(model) for model in cart_models]

        except Exception as e:
            raise InternalException() from e

    async def update_cart(self, cart_id: UUID, update_data: CartUpdate) -> Cart:
        """Actualizar un carrito"""
        try:
            stmt = select(CartModel).where(CartModel.cart_id == cart_id)
            result = await self.session.execute(stmt)
            cart_model = result.scalar_one_or_none()

            if not cart_model:
                raise NotFoundException()

            update_dict = update_data.model_dump(exclude_unset=True)

            for field, value in update_dict.items():
                if hasattr(cart_model, field) and value is not None:
                    setattr(cart_model, field, value)

            await self.session.commit()
            await self.session.refresh(cart_model)

            return self._model_to_entity(cart_model)

        except NotFoundException:
            raise
        except Exception as e:
            await self.session.rollback()
            raise InternalException() from e

    async def update_cart_totals(self, cart_id: UUID, total_amount: float, total_items: int) -> Cart:
        """Actualizar totales del carrito"""
        try:
            stmt = select(CartModel).where(CartModel.cart_id == cart_id)
            result = await self.session.execute(stmt)
            cart_model = result.scalar_one_or_none()

            if not cart_model:
                raise NotFoundException()

            cart_model.total_amount = total_amount
            cart_model.total_items = total_items

            await self.session.commit()
            await self.session.refresh(cart_model)

            return self._model_to_entity(cart_model)

        except NotFoundException:
            raise
        except Exception as e:
            await self.session.rollback()
            raise InternalException() from e

    async def mark_cart_as_completed(self, cart_id: UUID) -> Cart:
        """Marcar carrito como completado"""
        try:
            stmt = select(CartModel).where(CartModel.cart_id == cart_id)
            result = await self.session.execute(stmt)
            cart_model = result.scalar_one_or_none()

            if not cart_model:
                raise NotFoundException()

            cart_model.status = "completed"
            from datetime import datetime, timezone
            cart_model.completed_at = datetime.now(timezone.utc)

            await self.session.commit()
            await self.session.refresh(cart_model)

            return self._model_to_entity(cart_model)

        except NotFoundException:
            raise
        except Exception as e:
            await self.session.rollback()
            raise InternalException() from e

    async def mark_cart_as_abandoned(self, cart_id: UUID) -> Cart:
        """Marcar carrito como abandonado"""
        try:
            stmt = select(CartModel).where(CartModel.cart_id == cart_id)
            result = await self.session.execute(stmt)
            cart_model = result.scalar_one_or_none()

            if not cart_model:
                raise NotFoundException()

            cart_model.status = "abandoned"

            await self.session.commit()
            await self.session.refresh(cart_model)

            return self._model_to_entity(cart_model)

        except NotFoundException:
            raise
        except Exception as e:
            await self.session.rollback()
            raise InternalException() from e

    async def delete_cart(self, cart_id: UUID) -> bool:
        """Soft delete de un carrito"""
        try:
            stmt = select(CartModel).where(CartModel.cart_id == cart_id)
            result = await self.session.execute(stmt)
            cart_model = result.scalar_one_or_none()

            if not cart_model:
                return False

            cart_model.is_active = False
            await self.session.commit()

            return True

        except Exception as e:
            await self.session.rollback()
            raise InternalException() from e

    def _model_to_entity(self, cart_model: CartModel) -> Cart:
        """Convertir modelo SQLAlchemy a entidad de dominio"""
        return Cart(
            cart_id=cart_model.cart_id,
            user_id=cart_model.user_id,
            status=cart_model.status,
            total_amount=cart_model.total_amount,
            total_items=cart_model.total_items,
            is_active=cart_model.is_active,
            created_at=cart_model.created_at,
            updated_at=cart_model.updated_at,
            completed_at=cart_model.completed_at
        )
