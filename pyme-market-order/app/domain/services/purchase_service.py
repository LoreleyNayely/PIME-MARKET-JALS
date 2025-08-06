from typing import List, Optional
from uuid import UUID
from decimal import Decimal
from app.domain.entities.purchase import Purchase
from app.schemas.purchase_schema import PurchaseCreate
from app.infrastructure.db.repositories.purchase_repository import PurchaseRepository
from app.infrastructure.db.repositories.cart_repository import CartRepository
from app.infrastructure.db.repositories.cart_item_repository import CartItemRepository
from app.domain.exceptions.purchase_exception import (
    PurchaseNotFoundException,
    PurchaseAlreadyExistsException,
    InvalidAmountException,
    InvalidDiscountException,
    InvalidPaymentMethodException,
    PurchaseProcessingException,
    InsufficientStockException
)
from app.domain.exceptions.cart_exception import (
    CartNotFoundException,
    CartIsEmptyException,
    CartInactiveException,
    InvalidCartStatusException
)


class PurchaseService:
    def __init__(self, purchase_repository: PurchaseRepository, cart_repository: CartRepository,
                 cart_item_repository: CartItemRepository):
        self.purchase_repository = purchase_repository
        self.cart_repository = cart_repository
        self.cart_item_repository = cart_item_repository

    async def create_purchase(self, purchase_data: PurchaseCreate) -> Purchase:
        """Crear una nueva compra con validaciones de negocio"""
        cart = await self._validate_cart_for_purchase(purchase_data.cart_id)

        if await self.purchase_repository.purchase_exists_for_cart(purchase_data.cart_id):
            raise PurchaseAlreadyExistsException(str(purchase_data.cart_id))

        self._validate_financial_data(purchase_data)

        from app.domain.entities.purchase import Purchase as PurchaseEntity
        temp_purchase = PurchaseEntity(
            purchase_id=None,
            cart_id=purchase_data.cart_id,
            user_id=purchase_data.user_id,
            purchase_number=None,
            total_amount=purchase_data.total_amount,
            tax_amount=purchase_data.tax_amount,
            discount_amount=purchase_data.discount_amount,
            final_amount=purchase_data.total_amount -
            purchase_data.discount_amount + purchase_data.tax_amount,
            payment_method=purchase_data.payment_method,
            status="completed",
            purchased_at=None
        )
        temp_purchase.generate_purchase_number()

        purchase_data_with_number = PurchaseCreate(
            cart_id=purchase_data.cart_id,
            user_id=purchase_data.user_id,
            total_amount=purchase_data.total_amount,
            tax_amount=purchase_data.tax_amount,
            discount_amount=purchase_data.discount_amount,
            payment_method=purchase_data.payment_method,
            purchase_number=temp_purchase.purchase_number
        )

        purchase = await self.purchase_repository.create_purchase(purchase_data_with_number)

        await self.cart_repository.mark_cart_as_completed(purchase_data.cart_id)

        return purchase

    async def process_cart_purchase(self, cart_id: UUID, payment_method: str = None,
                                    discount_percentage: Decimal = None, tax_percentage: Decimal = None) -> Purchase:
        """Procesar compra completa de un carrito"""
        existing_purchase = await self.purchase_repository.get_purchase_by_cart_id(cart_id)
        if existing_purchase:
            if discount_percentage:
                existing_purchase.apply_discount(discount_percentage)

            if tax_percentage:
                existing_purchase.apply_tax(tax_percentage)

            if discount_percentage or tax_percentage:
                await self.purchase_repository.update_purchase_amounts(
                    existing_purchase.purchase_id,
                    float(existing_purchase.total_amount),
                    float(existing_purchase.tax_amount),
                    float(existing_purchase.discount_amount),
                    float(existing_purchase.final_amount)
                )

            return existing_purchase

        cart = await self._validate_cart_for_purchase(cart_id)

        cart_items = await self.cart_item_repository.get_cart_items_by_cart(cart_id)
        if not cart_items:
            raise CartIsEmptyException(str(cart_id))

        total_amount = sum(float(item.subtotal) for item in cart_items)

        purchase_data = PurchaseCreate(
            cart_id=cart_id,
            user_id=cart.user_id,
            total_amount=Decimal(str(total_amount)),
            tax_amount=Decimal('0.00'),
            discount_amount=Decimal('0.00'),
            payment_method=payment_method
        )

        purchase = await self.create_purchase(purchase_data)

        if discount_percentage:
            purchase.apply_discount(discount_percentage)

        if tax_percentage:
            purchase.apply_tax(tax_percentage)

        if discount_percentage or tax_percentage:
            await self.purchase_repository.update_purchase_amounts(
                purchase.purchase_id,
                float(purchase.total_amount),
                float(purchase.tax_amount),
                float(purchase.discount_amount),
                float(purchase.final_amount)
            )

        return purchase

    async def get_purchase_by_id(self, purchase_id: UUID) -> Purchase:
        """Obtener compra por ID"""
        purchase = await self.purchase_repository.get_purchase_by_id(purchase_id)
        if not purchase:
            raise PurchaseNotFoundException(purchase_id=str(purchase_id))
        return purchase

    async def get_purchase_by_cart_id(self, cart_id: UUID) -> Purchase:
        """Obtener compra por ID del carrito"""
        purchase = await self.purchase_repository.get_purchase_by_cart_id(cart_id)
        if not purchase:
            raise PurchaseNotFoundException()
        return purchase

    async def get_purchase_by_number(self, purchase_number: str) -> Purchase:
        """Obtener compra por número"""
        purchase = await self.purchase_repository.get_purchase_by_number(purchase_number)
        if not purchase:
            raise PurchaseNotFoundException(purchase_number=purchase_number)
        return purchase

    async def get_purchases_by_user(self, user_id: str) -> List[Purchase]:
        """Obtener todas las compras de un usuario"""
        return await self.purchase_repository.get_purchases_by_user(user_id)

    async def apply_discount_to_purchase(self, purchase_id: UUID, discount_amount: Decimal = None,
                                         discount_percentage: Decimal = None) -> Purchase:
        """Aplicar descuento a una compra"""
        purchase = await self.get_purchase_by_id(purchase_id)

        if discount_amount is not None:
            purchase.apply_fixed_discount(discount_amount)
        elif discount_percentage is not None:
            purchase.apply_discount(discount_percentage)
        else:
            raise InvalidDiscountException(
                0, "No discount amount or percentage provided")

        return await self.purchase_repository.update_purchase_amounts(
            purchase_id,
            float(purchase.total_amount),
            float(purchase.tax_amount),
            float(purchase.discount_amount),
            float(purchase.final_amount)
        )

    async def apply_tax_to_purchase(self, purchase_id: UUID, tax_percentage: Decimal) -> Purchase:
        """Aplicar impuesto a una compra"""
        purchase = await self.get_purchase_by_id(purchase_id)
        purchase.apply_tax(tax_percentage)

        return await self.purchase_repository.update_purchase_amounts(
            purchase_id,
            float(purchase.total_amount),
            float(purchase.tax_amount),
            float(purchase.discount_amount),
            float(purchase.final_amount)
        )

    async def update_payment_method(self, purchase_id: UUID, payment_method: str) -> Purchase:
        """Actualizar método de pago"""
        purchase = await self.get_purchase_by_id(purchase_id)

        self._validate_payment_method(payment_method)

        return await self.purchase_repository.update_payment_method(purchase_id, payment_method)

    async def get_purchase_summary(self, purchase_id: UUID) -> dict:
        """Obtener resumen completo de la compra"""
        purchase = await self.get_purchase_by_id(purchase_id)

        cart_items = await self.cart_item_repository.get_cart_items_by_cart(purchase.cart_id)

        return {
            "purchase_id": str(purchase.purchase_id),
            "purchase_number": purchase.purchase_number,
            "cart_id": str(purchase.cart_id),
            "user_id": purchase.user_id,
            "total_amount": float(purchase.total_amount),
            "tax_amount": float(purchase.tax_amount),
            "discount_amount": float(purchase.discount_amount),
            "final_amount": float(purchase.final_amount),
            "payment_method": purchase.payment_method,
            "status": purchase.status,
            "purchased_at": purchase.purchased_at.isoformat() if purchase.purchased_at else None,
            "items_count": len(cart_items),
            "total_items": sum(item.quantity for item in cart_items)
        }

    async def _validate_cart_for_purchase(self, cart_id: UUID):
        """Validar que el carrito puede ser comprado"""
        cart = await self.cart_repository.get_cart_by_id(cart_id)
        if not cart:
            raise CartNotFoundException(cart_id=str(cart_id))

        if not cart.can_be_purchased():
            if cart.status != "active":
                raise InvalidCartStatusException(cart.status, "active")
            if not cart.is_active:
                raise CartInactiveException(str(cart_id))
            if cart.is_empty():
                raise CartIsEmptyException(str(cart_id))

        return cart

    def _validate_financial_data(self, purchase_data: PurchaseCreate) -> None:
        """Validar datos financieros"""
        if purchase_data.total_amount <= 0:
            raise InvalidAmountException(
                "total amount", float(purchase_data.total_amount))

        if purchase_data.tax_amount < 0:
            raise InvalidAmountException(
                "tax amount", float(purchase_data.tax_amount))

        if purchase_data.discount_amount < 0:
            raise InvalidAmountException(
                "discount amount", float(purchase_data.discount_amount))

        if purchase_data.discount_amount > purchase_data.total_amount:
            raise InvalidDiscountException(
                float(purchase_data.discount_amount),
                float(purchase_data.total_amount)
            )

        if purchase_data.payment_method:
            self._validate_payment_method(purchase_data.payment_method)

    def _validate_payment_method(self, payment_method: str) -> None:
        """Validar método de pago"""
        allowed_methods = ['cash', 'card', 'transfer']
        if payment_method not in allowed_methods:
            raise InvalidPaymentMethodException(payment_method)


def get_purchase_service(purchase_repository: PurchaseRepository, cart_repository: CartRepository,
                         cart_item_repository: CartItemRepository) -> PurchaseService:
    """Factory function para obtener instancia del servicio"""
    return PurchaseService(purchase_repository, cart_repository, cart_item_repository)
