from typing import List, Optional
from uuid import UUID
from decimal import Decimal
from app.domain.entities.cart import Cart
from app.schemas.cart_schema import CartCreate, CartUpdate
from app.infrastructure.db.repositories.cart_repository import CartRepository
from app.infrastructure.db.repositories.cart_item_repository import CartItemRepository
from app.domain.exceptions.cart_exception import (
    CartNotFoundException,
    CartAlreadyCompletedException,
    CartIsEmptyException,
    CartInactiveException,
    CartAbandonedException,
    InvalidCartStatusException
)


class CartService:
    def __init__(self, cart_repository: CartRepository, cart_item_repository: CartItemRepository):
        self.cart_repository = cart_repository
        self.cart_item_repository = cart_item_repository

    async def create_cart(self, cart_data: CartCreate) -> Cart:
        """Crear un nuevo carrito con validaciones de negocio"""
        try:
            self._validate_user_id(cart_data.user_id)
            self._validate_cart_status(cart_data.status)

            existing_cart = await self.cart_repository.get_active_cart_by_user(cart_data.user_id)
            if existing_cart:
                return existing_cart

            return await self.cart_repository.create_cart(cart_data)

        except Exception as e:
            error_message = f"Failed to create cart for user {cart_data.user_id}: {type(e).__name__}: {str(e)}"
            raise Exception(error_message) from e

    async def get_cart_by_id(self, cart_id: UUID) -> Cart:
        """Obtener carrito por ID"""
        cart = await self.cart_repository.get_cart_by_id(cart_id)
        if not cart:
            raise CartNotFoundException(cart_id=str(cart_id))
        return cart

    async def get_or_create_active_cart(self, user_id: str) -> Cart:
        """Obtener carrito activo del usuario o crear uno nuevo"""
        cart = await self.cart_repository.get_active_cart_by_user(user_id)

        if cart:
            return cart

        cart_data = CartCreate(user_id=user_id, status="active")
        return await self.create_cart(cart_data)

    async def get_cart_with_items(self, cart_id: UUID) -> Cart:
        """Obtener carrito con sus items incluidos"""
        cart = await self.get_cart_by_id(cart_id)

        cart_items = await self.cart_item_repository.get_cart_items_by_cart(cart_id)
        cart.cart_items = cart_items

        cart.calculate_totals()

        return cart

    async def get_carts_by_user(self, user_id: str, include_inactive: bool = False) -> List[Cart]:
        """Obtener todos los carritos de un usuario"""
        return await self.cart_repository.get_carts_by_user(user_id, include_inactive)

    async def update_cart(self, cart_id: UUID, update_data: CartUpdate) -> Cart:
        """Actualizar un carrito con validaciones"""
        existing_cart = await self.get_cart_by_id(cart_id)

        self._validate_cart_can_be_modified(existing_cart)

        if update_data.status and update_data.status != existing_cart.status:
            self._validate_status_transition(
                existing_cart.status, update_data.status)

        return await self.cart_repository.update_cart(cart_id, update_data)

    async def refresh_cart_totals(self, cart_id: UUID) -> Cart:
        """Recalcular y actualizar totales del carrito"""
        cart = await self.get_cart_by_id(cart_id)

        total_amount, total_items = await self.cart_item_repository.calculate_cart_totals(cart_id)

        return await self.cart_repository.update_cart_totals(cart_id, total_amount, total_items)

    async def clear_cart(self, cart_id: UUID) -> Cart:
        """Vaciar carrito eliminando todos sus items"""
        cart = await self.get_cart_by_id(cart_id)

        self._validate_cart_can_be_modified(cart)

        await self.cart_item_repository.delete_cart_items_by_cart(cart_id)

        return await self.cart_repository.update_cart_totals(cart_id, 0.0, 0)

    async def complete_cart(self, cart_id: UUID) -> Cart:
        """Marcar carrito como completado"""
        cart = await self.get_cart_by_id(cart_id)

        if not cart.can_be_purchased():
            if cart.status != "active":
                raise InvalidCartStatusException(cart.status, "active")
            if not cart.is_active:
                raise CartInactiveException(str(cart_id))
            if cart.is_empty():
                raise CartIsEmptyException(str(cart_id))

        return await self.cart_repository.mark_cart_as_completed(cart_id)

    async def abandon_cart(self, cart_id: UUID) -> Cart:
        """Marcar carrito como abandonado"""
        cart = await self.get_cart_by_id(cart_id)

        if cart.status == "completed":
            raise CartAlreadyCompletedException(str(cart_id))

        return await self.cart_repository.mark_cart_as_abandoned(cart_id)

    async def delete_cart(self, cart_id: UUID) -> bool:
        """Eliminar carrito (soft delete)"""
        cart = await self.get_cart_by_id(cart_id)

        if cart.status == "completed":
            raise CartAlreadyCompletedException(str(cart_id))

        return await self.cart_repository.delete_cart(cart_id)

    def _validate_user_id(self, user_id: str) -> None:
        """Validar ID de usuario"""
        if not user_id or not user_id.strip():
            raise Exception("User ID cannot be empty")

        if len(user_id.strip()) < 2:
            raise Exception("User ID must be at least 2 characters long")

    def _validate_cart_status(self, status: str) -> None:
        """Validar estado del carrito"""
        allowed_statuses = ['active', 'completed', 'abandoned']
        if status not in allowed_statuses:
            raise Exception(
                f"Invalid cart status. Allowed: {', '.join(allowed_statuses)}")

    def _validate_cart_can_be_modified(self, cart: Cart) -> None:
        """Validar que el carrito puede ser modificado"""
        if cart.status == "completed":
            raise CartAlreadyCompletedException(str(cart.cart_id))

        if cart.status == "abandoned":
            raise CartAbandonedException(str(cart.cart_id))

        if not cart.is_active:
            raise CartInactiveException(str(cart.cart_id))

    def _validate_status_transition(self, current_status: str, new_status: str) -> None:
        """Validar transición de estados"""
        valid_transitions = {
            'active': ['completed', 'abandoned'],
            'completed': [],
            'abandoned': ['active']
        }

        if new_status not in valid_transitions.get(current_status, []):
            raise InvalidCartStatusException(current_status, new_status)


def get_cart_service(cart_repository: CartRepository, cart_item_repository: CartItemRepository) -> CartService:
    """Factory function para obtener instancia del servicio"""
    return CartService(cart_repository, cart_item_repository)
