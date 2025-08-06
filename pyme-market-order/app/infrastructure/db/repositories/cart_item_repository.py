from typing import Optional, List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.exc import IntegrityError
from app.domain.entities.cart_item import CartItem
from app.infrastructure.db.models.cart_item_model import CartItemModel
from app.schemas.cart_item_schema import CartItemCreate, CartItemUpdate
from app.domain.exceptions.not_found_exception import NotFoundException
from app.domain.exceptions.internal_exception import InternalException


class CartItemRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_cart_item(self, cart_id: UUID, item_data: CartItemCreate) -> CartItem:
        """Crear un nuevo item en el carrito"""
        try:
            subtotal = item_data.unit_price * item_data.quantity

            cart_item_model = CartItemModel(
                cart_id=cart_id,
                product_id=item_data.product_id,
                product_name=item_data.product_name,
                product_sku=item_data.product_sku.upper().strip(),
                unit_price=item_data.unit_price,
                quantity=item_data.quantity,
                subtotal=subtotal
            )

            self.session.add(cart_item_model)
            await self.session.commit()
            await self.session.refresh(cart_item_model)

            return self._model_to_entity(cart_item_model)

        except IntegrityError as e:
            await self.session.rollback()
            raise InternalException() from e
        except Exception as e:
            await self.session.rollback()
            raise InternalException() from e

    async def get_cart_item_by_id(self, cart_item_id: UUID) -> Optional[CartItem]:
        """Obtener item del carrito por ID"""
        try:
            stmt = select(CartItemModel).where(
                CartItemModel.cart_item_id == cart_item_id)
            result = await self.session.execute(stmt)
            cart_item_model = result.scalar_one_or_none()

            if cart_item_model:
                return self._model_to_entity(cart_item_model)
            return None

        except Exception as e:
            raise InternalException() from e

    async def get_cart_items_by_cart(self, cart_id: UUID) -> List[CartItem]:
        """Obtener todos los items de un carrito"""
        try:
            stmt = select(CartItemModel).where(
                CartItemModel.cart_id == cart_id
            ).order_by(CartItemModel.added_at.asc())

            result = await self.session.execute(stmt)
            cart_item_models = result.scalars().all()

            return [self._model_to_entity(model) for model in cart_item_models]

        except Exception as e:
            raise InternalException() from e

    async def get_cart_item_by_product(self, cart_id: UUID, product_id: UUID) -> Optional[CartItem]:
        """Obtener item específico por producto en un carrito"""
        try:
            stmt = select(CartItemModel).where(
                and_(
                    CartItemModel.cart_id == cart_id,
                    CartItemModel.product_id == product_id
                )
            )
            result = await self.session.execute(stmt)
            cart_item_model = result.scalar_one_or_none()

            if cart_item_model:
                return self._model_to_entity(cart_item_model)
            return None

        except Exception as e:
            raise InternalException() from e

    async def update_cart_item_quantity(self, cart_item_id: UUID, new_quantity: int) -> CartItem:
        """Actualizar cantidad de un item del carrito"""
        try:
            stmt = select(CartItemModel).where(
                CartItemModel.cart_item_id == cart_item_id)
            result = await self.session.execute(stmt)
            cart_item_model = result.scalar_one_or_none()

            if not cart_item_model:
                raise NotFoundException()

            cart_item_model.quantity = new_quantity
            cart_item_model.subtotal = cart_item_model.unit_price * new_quantity

            await self.session.commit()
            await self.session.refresh(cart_item_model)

            return self._model_to_entity(cart_item_model)

        except NotFoundException:
            raise
        except Exception as e:
            await self.session.rollback()
            raise InternalException() from e

    async def update_cart_item(self, cart_item_id: UUID, update_data: CartItemUpdate) -> CartItem:
        """Actualizar un item del carrito"""
        try:
            stmt = select(CartItemModel).where(
                CartItemModel.cart_item_id == cart_item_id)
            result = await self.session.execute(stmt)
            cart_item_model = result.scalar_one_or_none()

            if not cart_item_model:
                raise NotFoundException()

            if update_data.quantity is not None:
                cart_item_model.quantity = update_data.quantity
                cart_item_model.subtotal = cart_item_model.unit_price * update_data.quantity

            await self.session.commit()
            await self.session.refresh(cart_item_model)

            return self._model_to_entity(cart_item_model)

        except NotFoundException:
            raise
        except Exception as e:
            await self.session.rollback()
            raise InternalException() from e

    async def delete_cart_item(self, cart_item_id: UUID) -> bool:
        """Eliminar un item del carrito"""
        try:
            stmt = select(CartItemModel).where(
                CartItemModel.cart_item_id == cart_item_id)
            result = await self.session.execute(stmt)
            cart_item_model = result.scalar_one_or_none()

            if not cart_item_model:
                return False

            await self.session.delete(cart_item_model)
            await self.session.commit()

            return True

        except Exception as e:
            await self.session.rollback()
            raise InternalException() from e

    async def delete_cart_items_by_cart(self, cart_id: UUID) -> bool:
        """Eliminar todos los items de un carrito"""
        try:
            stmt = select(CartItemModel).where(
                CartItemModel.cart_id == cart_id)
            result = await self.session.execute(stmt)
            cart_items = result.scalars().all()

            for item in cart_items:
                await self.session.delete(item)

            await self.session.commit()
            return True

        except Exception as e:
            await self.session.rollback()
            raise InternalException() from e

    async def count_cart_items(self, cart_id: UUID) -> int:
        """Contar items en un carrito"""
        try:
            stmt = select(CartItemModel).where(
                CartItemModel.cart_id == cart_id)
            result = await self.session.execute(stmt)
            cart_items = result.scalars().all()

            return len(cart_items)

        except Exception as e:
            raise InternalException() from e

    async def calculate_cart_totals(self, cart_id: UUID) -> tuple[float, int]:
        """Calcular totales del carrito (amount, items)"""
        try:
            stmt = select(CartItemModel).where(
                CartItemModel.cart_id == cart_id)
            result = await self.session.execute(stmt)
            cart_items = result.scalars().all()

            total_amount = sum(float(item.subtotal) for item in cart_items)
            total_items = sum(item.quantity for item in cart_items)

            return total_amount, total_items

        except Exception as e:
            raise InternalException() from e

    def _model_to_entity(self, cart_item_model: CartItemModel) -> CartItem:
        """Convertir modelo SQLAlchemy a entidad de dominio"""
        return CartItem(
            cart_item_id=cart_item_model.cart_item_id,
            cart_id=cart_item_model.cart_id,
            product_id=cart_item_model.product_id,
            product_name=cart_item_model.product_name,
            product_sku=cart_item_model.product_sku,
            unit_price=cart_item_model.unit_price,
            quantity=cart_item_model.quantity,
            subtotal=cart_item_model.subtotal,
            added_at=cart_item_model.added_at,
            updated_at=cart_item_model.updated_at
        )
