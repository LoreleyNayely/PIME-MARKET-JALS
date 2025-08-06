from typing import Optional, Dict, Any, List, TYPE_CHECKING
from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID
from app.core.camel_case_config import CamelBaseModel

if TYPE_CHECKING:
    from .purchase import Purchase
    from .cart_item import CartItem


class Receipt(CamelBaseModel):
    receipt_id: Optional[UUID] = None
    purchase_id: UUID
    receipt_data: Dict[str, Any] = {}
    generated_at: Optional[datetime] = None

    purchase: Optional['Purchase'] = None

    def generate_receipt_data(self, purchase: 'Purchase', cart_items: List['CartItem']) -> None:
        """Generar los datos del comprobante basado en la compra y items"""
        if not purchase.purchase_number:
            purchase.generate_purchase_number()

        self.receipt_data = {
            "purchase_number": purchase.purchase_number,
            "user_id": purchase.user_id,
            "purchase_date": purchase.purchased_at.isoformat() if purchase.purchased_at else datetime.now(timezone.utc).isoformat(),
            "total_amount": float(purchase.total_amount),
            "tax_amount": float(purchase.tax_amount),
            "discount_amount": float(purchase.discount_amount),
            "final_amount": float(purchase.final_amount),
            "payment_method": purchase.payment_method or "not_specified",
            "items": [
                {
                    "product_id": str(item.product_id),
                    "product_name": item.product_name,
                    "product_sku": item.product_sku,
                    "unit_price": float(item.unit_price),
                    "quantity": item.quantity,
                    "subtotal": float(item.subtotal)
                }
                for item in cart_items
            ],
            "summary": {
                "total_items": len(cart_items),
                "total_quantity": sum(item.quantity for item in cart_items),
                "subtotal": float(purchase.total_amount),
                "discount": float(purchase.discount_amount),
                "tax": float(purchase.tax_amount),
                "final_total": float(purchase.final_amount)
            }
        }

    def get_formatted_receipt(self) -> str:
        """Generar comprobante formateado como texto"""
        if not self.receipt_data:
            return "No receipt data available"

        lines = []
        lines.append("=" * 50)
        lines.append("           PYME MARKET")
        lines.append("         COMPROBANTE DE COMPRA")
        lines.append("=" * 50)
        lines.append(
            f"Número: {self.receipt_data.get('purchase_number', 'N/A')}")
        lines.append(f"Fecha: {self.receipt_data.get('purchase_date', 'N/A')}")
        lines.append(f"Cliente: {self.receipt_data.get('user_id', 'N/A')}")
        lines.append("-" * 50)
        lines.append("ITEMS:")

        for item in self.receipt_data.get('items', []):
            lines.append(f"{item['product_name']} ({item['product_sku']})")
            lines.append(
                f"  {item['quantity']} x ${item['unit_price']:.2f} = ${item['subtotal']:.2f}")

        lines.append("-" * 50)
        summary = self.receipt_data.get('summary', {})
        lines.append(f"Subtotal: ${summary.get('subtotal', 0):.2f}")
        if summary.get('discount', 0) > 0:
            lines.append(f"Descuento: -${summary.get('discount', 0):.2f}")
        if summary.get('tax', 0) > 0:
            lines.append(f"Impuestos: ${summary.get('tax', 0):.2f}")
        lines.append("=" * 50)
        lines.append(f"TOTAL: ${summary.get('final_total', 0):.2f}")
        lines.append(
            f"Método de pago: {self.receipt_data.get('payment_method', 'N/A')}")
        lines.append("=" * 50)
        lines.append("¡Gracias por su compra!")

        return "\n".join(lines)

    def get_total_amount(self) -> Decimal:
        """Obtener el monto total del recibo"""
        summary = self.receipt_data.get('summary', {})
        return Decimal(str(summary.get('final_total', 0)))

    def get_items_count(self) -> int:
        """Obtener la cantidad de items en el recibo"""
        return len(self.receipt_data.get('items', []))
