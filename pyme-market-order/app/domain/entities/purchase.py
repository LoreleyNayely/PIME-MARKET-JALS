from typing import Optional, TYPE_CHECKING
from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID
from app.core.camel_case_config import CamelBaseModel

if TYPE_CHECKING:
    from .cart import Cart
    from .receipt import Receipt


class Purchase(CamelBaseModel):
    purchase_id: Optional[UUID] = None
    cart_id: UUID
    user_id: str
    purchase_number: Optional[str] = None
    total_amount: Decimal
    tax_amount: Decimal = Decimal('0.00')
    discount_amount: Decimal = Decimal('0.00')
    final_amount: Decimal = Decimal('0.00')
    payment_method: Optional[str] = None
    status: str = "completed"
    purchased_at: Optional[datetime] = None

    cart: Optional['Cart'] = None
    receipt: Optional['Receipt'] = None

    def calculate_final_amount(self) -> None:
        """Calcular el monto final: total - descuento + impuestos"""
        self.final_amount = self.total_amount - self.discount_amount + self.tax_amount

    def apply_discount(self, discount_percentage: Decimal) -> None:
        """Aplicar descuento por porcentaje"""
        if discount_percentage < 0 or discount_percentage > 100:
            raise ValueError("Discount percentage must be between 0 and 100")

        self.discount_amount = (self.total_amount * discount_percentage) / 100
        self.calculate_final_amount()

    def apply_fixed_discount(self, discount_amount: Decimal) -> None:
        """Aplicar descuento fijo"""
        if discount_amount < 0:
            raise ValueError("Discount amount cannot be negative")
        if discount_amount > self.total_amount:
            raise ValueError("Discount cannot exceed total amount")

        self.discount_amount = discount_amount
        self.calculate_final_amount()

    def apply_tax(self, tax_percentage: Decimal) -> None:
        """Aplicar impuesto por porcentaje"""
        if tax_percentage < 0:
            raise ValueError("Tax percentage cannot be negative")

        taxable_amount = self.total_amount - self.discount_amount
        self.tax_amount = (taxable_amount * tax_percentage) / 100
        self.calculate_final_amount()

    def set_payment_method(self, method: str) -> None:
        """Establecer método de pago"""
        allowed_methods = ['cash', 'card', 'transfer']
        if method not in allowed_methods:
            raise ValueError(
                f"Payment method must be one of: {', '.join(allowed_methods)}")

        self.payment_method = method

    def generate_purchase_number(self) -> str:
        """Generar número único de compra"""
        if not self.purchased_at:
            self.purchased_at = datetime.now(timezone.utc)

        timestamp = self.purchased_at.strftime("%Y%m%d%H%M%S")
        short_id = str(
            self.purchase_id)[-8:] if self.purchase_id else "00000000"
        self.purchase_number = f"PUR-{timestamp}-{short_id}"
        return self.purchase_number

    def is_completed(self) -> bool:
        """Verificar si la compra está completada"""
        return self.status == "completed"
