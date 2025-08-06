from typing import Optional, List, TYPE_CHECKING
from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID
from app.core.camel_case_config import CamelBaseModel

if TYPE_CHECKING:
    from .cart_item import CartItem
    from .purchase import Purchase


class Cart(CamelBaseModel):
    cart_id: Optional[UUID] = None
    user_id: str
    status: str = "active"
    total_amount: Decimal = Decimal('0.00')
    total_items: int = 0
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    cart_items: Optional[List['CartItem']] = None
    purchase: Optional['Purchase'] = None

    def calculate_totals(self) -> None:
        """Recalcular totales del carrito basado en los items"""
        if self.cart_items is not None:
            self.total_amount = sum(item.subtotal for item in self.cart_items)
            self.total_items = sum(item.quantity for item in self.cart_items)
        else:
            self.total_amount = Decimal('0.00')
            self.total_items = 0

    def is_empty(self) -> bool:
        """Verificar si el carrito está vacío"""
        return self.total_items == 0

    def can_be_purchased(self) -> bool:
        """Verificar si el carrito puede ser comprado"""
        return (
            self.is_active and
            self.status == "active" and
            not self.is_empty()
        )

    def mark_as_completed(self) -> None:
        """Marcar el carrito como completado"""
        self.status = "completed"
        self.completed_at = datetime.now(timezone.utc)

    def mark_as_abandoned(self) -> None:
        """Marcar el carrito como abandonado"""
        self.status = "abandoned"
