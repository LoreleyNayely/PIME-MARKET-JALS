from typing import List, Optional
from uuid import UUID
from decimal import Decimal
from app.domain.entities.cart_item import CartItem
from app.schemas.cart_item_schema import CartItemCreate, CartItemUpdate
from app.infrastructure.db.repositories.cart_item_repository import CartItemRepository
from app.infrastructure.db.repositories.cart_repository import CartRepository
from app.domain.exceptions.cart_item_exception import (
    CartItemNotFoundException,
    InvalidQuantityException,
    ProductAlreadyInCartException,
    InvalidPriceException,
    ProductDataIncompleteException
)
from app.domain.exceptions.cart_exception import (
    CartNotFoundException,
    CartInactiveException,
    CartAlreadyCompletedException
)


class CartItemService:
    def __init__(self, cart_item_repository: CartItemRepository, cart_repository: CartRepository):
        self.cart_item_repository = cart_item_repository
        self.cart_repository = cart_repository

    async def add_item_to_cart(self, cart_id: UUID, item_data: CartItemCreate) -> CartItem:
        """Agregar item al carrito con validaciones de negocio"""
        cart = await self._get_and_validate_cart(cart_id)

        self._validate_product_data(item_data)

        existing_item = await self.cart_item_repository.get_cart_item_by_product(cart_id, item_data.product_id)
        if existing_item:
            new_quantity = existing_item.quantity + item_data.quantity
            return await self.update_item_quantity(existing_item.cart_item_id, new_quantity)

        cart_item = await self.cart_item_repository.create_cart_item(cart_id, item_data)

        await self._refresh_cart_totals(cart_id)

        return cart_item

    async def get_cart_item_by_id(self, cart_item_id: UUID) -> CartItem:
        """Obtener item del carrito por ID"""
        cart_item = await self.cart_item_repository.get_cart_item_by_id(cart_item_id)
        if not cart_item:
            raise CartItemNotFoundException(cart_item_id=str(cart_item_id))
        return cart_item

    async def get_cart_items(self, cart_id: UUID) -> List[CartItem]:
        """Obtener todos los items de un carrito"""
        await self._get_and_validate_cart(cart_id, check_modifiable=False)

        return await self.cart_item_repository.get_cart_items_by_cart(cart_id)

    async def update_item_quantity(self, cart_item_id: UUID, new_quantity: int) -> CartItem:
        """Actualizar cantidad de un item"""
        self._validate_quantity(new_quantity)

        cart_item = await self.get_cart_item_by_id(cart_item_id)

        await self._get_and_validate_cart(cart_item.cart_id)

        updated_item = await self.cart_item_repository.update_cart_item_quantity(cart_item_id, new_quantity)

        await self._refresh_cart_totals(cart_item.cart_id)

        return updated_item

    async def update_cart_item(self, cart_item_id: UUID, update_data: CartItemUpdate) -> CartItem:
        """Actualizar un item del carrito"""
        cart_item = await self.get_cart_item_by_id(cart_item_id)

        await self._get_and_validate_cart(cart_item.cart_id)

        if update_data.quantity is not None:
            self._validate_quantity(update_data.quantity)

        updated_item = await self.cart_item_repository.update_cart_item(cart_item_id, update_data)

        await self._refresh_cart_totals(cart_item.cart_id)

        return updated_item

    async def remove_item_from_cart(self, cart_item_id: UUID) -> bool:
        """Eliminar item del carrito"""
        cart_item = await self.get_cart_item_by_id(cart_item_id)

        await self._get_and_validate_cart(cart_item.cart_id)

        success = await self.cart_item_repository.delete_cart_item(cart_item_id)

        if success:
            await self._refresh_cart_totals(cart_item.cart_id)

        return success

    async def remove_product_from_cart(self, cart_id: UUID, product_id: UUID) -> bool:
        """Eliminar producto específico del carrito"""
        await self._get_and_validate_cart(cart_id)

        cart_item = await self.cart_item_repository.get_cart_item_by_product(cart_id, product_id)
        if not cart_item:
            raise CartItemNotFoundException(product_id=str(product_id))

        success = await self.cart_item_repository.delete_cart_item(cart_item.cart_item_id)

        if success:
            await self._refresh_cart_totals(cart_id)

        return success

    async def clear_cart_items(self, cart_id: UUID) -> bool:
        """Eliminar todos los items de un carrito"""
        await self._get_and_validate_cart(cart_id)

        success = await self.cart_item_repository.delete_cart_items_by_cart(cart_id)

        if success:
            await self.cart_repository.update_cart_totals(cart_id, 0.0, 0)

        return success

    async def get_cart_summary(self, cart_id: UUID) -> dict:
        """Obtener resumen del carrito"""
        await self._get_and_validate_cart(cart_id, check_modifiable=False)

        total_amount, total_items = await self.cart_item_repository.calculate_cart_totals(cart_id)
        items_count = await self.cart_item_repository.count_cart_items(cart_id)

        return {
            "cart_id": str(cart_id),
            "total_amount": total_amount,
            "total_items": total_items,
            "items_count": items_count,
            "is_empty": total_items == 0
        }

    async def _get_and_validate_cart(self, cart_id: UUID, check_modifiable: bool = True):
        """Obtener y validar carrito"""
        cart = await self.cart_repository.get_cart_by_id(cart_id)
        if not cart:
            raise CartNotFoundException(cart_id=str(cart_id))

        if check_modifiable:
            self._validate_cart_can_be_modified(cart)

        return cart

    async def _refresh_cart_totals(self, cart_id: UUID) -> None:
        """Refrescar totales del carrito"""
        total_amount, total_items = await self.cart_item_repository.calculate_cart_totals(cart_id)
        await self.cart_repository.update_cart_totals(cart_id, total_amount, total_items)

    def _validate_product_data(self, item_data: CartItemCreate) -> None:
        """Validar datos del producto"""
        missing_fields = []

        if not item_data.product_name or not item_data.product_name.strip():
            missing_fields.append("product_name")

        if not item_data.product_sku or not item_data.product_sku.strip():
            missing_fields.append("product_sku")

        if item_data.unit_price <= 0:
            raise InvalidPriceException(float(item_data.unit_price))

        if item_data.quantity <= 0:
            raise InvalidQuantityException(item_data.quantity)

        if missing_fields:
            raise ProductDataIncompleteException(missing_fields)

    def _validate_quantity(self, quantity: int) -> None:
        """Validar cantidad"""
        if quantity <= 0:
            raise InvalidQuantityException(quantity)

        if quantity > 999:
            raise InvalidQuantityException(quantity, max_quantity=999)

    def _validate_cart_can_be_modified(self, cart) -> None:
        """Validar que el carrito puede ser modificado"""
        if cart.status == "completed":
            raise CartAlreadyCompletedException(str(cart.cart_id))

        if not cart.is_active:
            raise CartInactiveException(str(cart.cart_id))


def get_cart_item_service(cart_item_repository: CartItemRepository, cart_repository: CartRepository) -> CartItemService:
    """Factory function para obtener instancia del servicio"""
    return CartItemService(cart_item_repository, cart_repository)
