from typing import Optional
from datetime import datetime
from decimal import Decimal
from uuid import UUID
from app.core.camel_case_config import CamelBaseModel


class CartItem(CamelBaseModel):
    cart_item_id: Optional[UUID] = None
    cart_id: Optional[UUID] = None
    product_id: UUID
    product_name: str
    product_sku: str
    unit_price: Decimal
    quantity: int
    subtotal: Decimal = Decimal('0.00')
    added_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def calculate_subtotal(self) -> None:
        """Calcular el subtotal del item"""
        self.subtotal = self.unit_price * self.quantity

    def update_quantity(self, new_quantity: int) -> None:
        """Actualizar la cantidad y recalcular subtotal"""
        if new_quantity <= 0:
            raise ValueError("Quantity must be greater than 0")
        if new_quantity > 999:
            raise ValueError("Quantity cannot exceed 999 units")

        self.quantity = new_quantity
        self.calculate_subtotal()

    def is_same_product(self, product_id: UUID) -> bool:
        """Verificar si el item corresponde al mismo producto"""
        return self.product_id == product_id

    def get_total_value(self) -> Decimal:
        """Obtener el valor total del item"""
        return self.subtotal
