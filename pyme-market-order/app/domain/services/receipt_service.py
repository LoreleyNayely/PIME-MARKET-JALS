from typing import Optional
from uuid import UUID
from app.domain.entities.receipt import Receipt
from app.infrastructure.db.repositories.receipt_repository import ReceiptRepository
from app.infrastructure.db.repositories.purchase_repository import PurchaseRepository
from app.infrastructure.db.repositories.cart_item_repository import CartItemRepository
from app.domain.exceptions.receipt_exception import (
    ReceiptNotFoundException,
    ReceiptAlreadyExistsException,
    ReceiptGenerationException,
    InvalidReceiptDataException
)
from app.domain.exceptions.purchase_exception import PurchaseNotFoundException


class ReceiptService:
    def __init__(self, receipt_repository: ReceiptRepository, purchase_repository: PurchaseRepository,
                 cart_item_repository: CartItemRepository):
        self.receipt_repository = receipt_repository
        self.purchase_repository = purchase_repository
        self.cart_item_repository = cart_item_repository

    async def generate_receipt(self, purchase_id: UUID) -> Receipt:
        """Generar recibo para una compra"""
        try:
            purchase = await self.purchase_repository.get_purchase_by_id(purchase_id)
            if not purchase:
                raise PurchaseNotFoundException(purchase_id=str(purchase_id))

            if await self.receipt_repository.receipt_exists_for_purchase(purchase_id):
                raise ReceiptAlreadyExistsException(str(purchase_id))

            cart_items = await self.cart_item_repository.get_cart_items_by_cart(purchase.cart_id)

            receipt = Receipt(purchase_id=purchase_id)
            receipt.generate_receipt_data(purchase, cart_items)

            return await self.receipt_repository.create_receipt(purchase_id, receipt.receipt_data)

        except (PurchaseNotFoundException, ReceiptAlreadyExistsException):
            raise
        except Exception as e:
            raise ReceiptGenerationException(str(purchase_id), str(e)) from e

    async def get_receipt_by_id(self, receipt_id: UUID) -> Receipt:
        """Obtener recibo por ID"""
        receipt = await self.receipt_repository.get_receipt_by_id(receipt_id)
        if not receipt:
            raise ReceiptNotFoundException(receipt_id=str(receipt_id))
        return receipt

    async def get_receipt_by_purchase_id(self, purchase_id: UUID) -> Receipt:
        """Obtener recibo por ID de compra"""
        receipt = await self.receipt_repository.get_receipt_by_purchase_id(purchase_id)
        if not receipt:
            raise ReceiptNotFoundException(purchase_id=str(purchase_id))
        return receipt

    async def get_or_generate_receipt(self, purchase_id: UUID) -> Receipt:
        """Obtener recibo existente o generar uno nuevo"""
        try:
            existing_receipt = await self.receipt_repository.get_receipt_by_purchase_id(purchase_id)
            if existing_receipt:
                return existing_receipt

            purchase = await self.purchase_repository.get_purchase_by_id(purchase_id)
            if not purchase:
                raise PurchaseNotFoundException(purchase_id=str(purchase_id))

            cart_items = await self.cart_item_repository.get_cart_items_by_cart(purchase.cart_id)

            receipt = Receipt(purchase_id=purchase_id)
            receipt.generate_receipt_data(purchase, cart_items)

            try:
                return await self.receipt_repository.create_receipt(purchase_id, receipt.receipt_data)
            except Exception as e:
                existing_receipt = await self.receipt_repository.get_receipt_by_purchase_id(purchase_id)
                if existing_receipt:
                    return existing_receipt
                raise ReceiptGenerationException(
                    str(purchase_id), str(e)) from e

        except PurchaseNotFoundException:
            raise
        except Exception as e:
            raise ReceiptGenerationException(str(purchase_id), str(e)) from e

    async def regenerate_receipt(self, purchase_id: UUID) -> Receipt:
        """Regenerar recibo para una compra"""
        try:
            purchase = await self.purchase_repository.get_purchase_by_id(purchase_id)
            if not purchase:
                raise PurchaseNotFoundException(purchase_id=str(purchase_id))

            cart_items = await self.cart_item_repository.get_cart_items_by_cart(purchase.cart_id)

            receipt = Receipt(purchase_id=purchase_id)
            receipt.generate_receipt_data(purchase, cart_items)

            existing_receipt = await self.receipt_repository.get_receipt_by_purchase_id(purchase_id)

            if existing_receipt:
                return await self.receipt_repository.update_receipt_data(
                    existing_receipt.receipt_id,
                    receipt.receipt_data
                )
            else:
                return await self.receipt_repository.create_receipt(purchase_id, receipt.receipt_data)

        except PurchaseNotFoundException:
            raise
        except Exception as e:
            raise ReceiptGenerationException(str(purchase_id), str(e)) from e

    async def get_formatted_receipt(self, purchase_id: UUID) -> str:
        """Obtener recibo formateado como texto"""
        receipt = await self.get_receipt_by_purchase_id(purchase_id)

        receipt_entity = Receipt(
            receipt_id=receipt.receipt_id,
            purchase_id=receipt.purchase_id,
            receipt_data=receipt.receipt_data,
            generated_at=receipt.generated_at
        )

        return receipt_entity.get_formatted_receipt()

    async def get_receipt_summary(self, purchase_id: UUID) -> dict:
        """Obtener resumen del recibo"""
        receipt = await self.get_receipt_by_purchase_id(purchase_id)

        receipt_data = receipt.receipt_data
        summary = receipt_data.get('summary', {})

        return {
            "receipt_id": str(receipt.receipt_id),
            "purchase_id": str(receipt.purchase_id),
            "purchase_number": receipt_data.get('purchase_number'),
            "user_id": receipt_data.get('user_id'),
            "purchase_date": receipt_data.get('purchase_date'),
            "total_amount": summary.get('final_total', 0),
            "items_count": summary.get('total_items', 0),
            "total_quantity": summary.get('total_quantity', 0),
            "payment_method": receipt_data.get('payment_method'),
            "generated_at": receipt.generated_at.isoformat() if receipt.generated_at else None
        }

    async def delete_receipt(self, receipt_id: UUID) -> bool:
        """Eliminar un recibo"""
        receipt = await self.get_receipt_by_id(receipt_id)
        return await self.receipt_repository.delete_receipt(receipt_id)

    def _validate_receipt_data(self, receipt_data: dict) -> None:
        """Validar estructura de datos del recibo"""
        required_fields = [
            'purchase_number', 'user_id', 'purchase_date',
            'total_amount', 'final_amount', 'items', 'summary'
        ]

        missing_fields = []
        invalid_fields = []

        for field in required_fields:
            if field not in receipt_data:
                missing_fields.append(field)

        if 'items' in receipt_data:
            if not isinstance(receipt_data['items'], list):
                invalid_fields.append('items (must be a list)')

        if 'summary' in receipt_data:
            if not isinstance(receipt_data['summary'], dict):
                invalid_fields.append('summary (must be a dictionary)')

        if missing_fields or invalid_fields:
            raise InvalidReceiptDataException(missing_fields, invalid_fields)


def get_receipt_service(receipt_repository: ReceiptRepository, purchase_repository: PurchaseRepository,
                        cart_item_repository: CartItemRepository) -> ReceiptService:
    """Factory function para obtener instancia del servicio"""
    return ReceiptService(receipt_repository, purchase_repository, cart_item_repository)
