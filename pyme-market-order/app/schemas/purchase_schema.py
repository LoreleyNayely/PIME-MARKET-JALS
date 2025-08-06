from typing import Optional, TYPE_CHECKING
from datetime import datetime
from decimal import Decimal
from uuid import UUID
from pydantic import Field, validator
from app.core.camel_case_config import CamelBaseModel

if TYPE_CHECKING:
    from .receipt_schema import ReceiptResponse


class PurchaseBase(CamelBaseModel):
    """Base schema con campos comunes de la compra"""
    user_id: str = Field(..., min_length=1, max_length=255,
                         description="User ID who made the purchase")
    total_amount: Decimal = Field(..., gt=0,
                                  description="Total amount before taxes and discounts")
    tax_amount: Decimal = Field(default=Decimal('0.00'), ge=0,
                                description="Tax amount applied")
    discount_amount: Decimal = Field(default=Decimal('0.00'), ge=0,
                                     description="Discount amount applied")
    payment_method: Optional[str] = Field(None, max_length=50,
                                          description="Payment method: cash, card, transfer")

    @validator('total_amount', 'tax_amount', 'discount_amount')
    def validate_amounts(cls, v):
        if v < 0:
            raise ValueError('Amount cannot be negative')
        if v.as_tuple().exponent < -2:
            raise ValueError('Amount can have maximum 2 decimal places')
        return v

    @validator('payment_method')
    def validate_payment_method(cls, v):
        if v is not None:
            allowed_methods = ['cash', 'card', 'transfer']
            if v not in allowed_methods:
                raise ValueError(
                    f'Payment method must be one of: {", ".join(allowed_methods)}')
        return v

    @validator('user_id')
    def validate_user_id(cls, v):
        v = v.strip()
        if not v:
            raise ValueError('User ID cannot be empty')
        return v


class PurchaseCreate(PurchaseBase):
    """Schema para crear una compra"""
    cart_id: UUID = Field(..., description="Cart ID to purchase")
    purchase_number: Optional[str] = Field(
        None, max_length=50, description="Purchase number (auto-generated if not provided)")


class PurchaseResponse(PurchaseBase):
    """Schema para respuesta de compra"""
    purchase_id: UUID
    cart_id: UUID
    purchase_number: str
    final_amount: Decimal
    status: str
    purchased_at: datetime

    class Config:
        from_attributes = True


class PurchaseWithReceiptResponse(PurchaseResponse):
    """Schema para compra con su recibo"""
    receipt: Optional['ReceiptResponse'] = None

    class Config:
        from_attributes = True


class PurchaseListResponse(CamelBaseModel):
    """Schema para lista de compras"""
    purchases: list[PurchaseResponse]
    total: int
