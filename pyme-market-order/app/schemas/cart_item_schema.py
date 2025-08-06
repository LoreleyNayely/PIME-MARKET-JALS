from typing import Optional
from datetime import datetime
from decimal import Decimal
from uuid import UUID
from pydantic import Field, validator
from app.core.camel_case_config import CamelBaseModel


class CartItemBase(CamelBaseModel):
    """Base schema con campos comunes del item del carrito"""
    product_id: UUID = Field(..., description="Product ID reference")
    product_name: str = Field(..., min_length=1, max_length=255,
                              description="Product name snapshot")
    product_sku: str = Field(..., min_length=1, max_length=100,
                             description="Product SKU snapshot")
    unit_price: Decimal = Field(..., gt=0,
                                description="Unit price at the time of adding")
    quantity: int = Field(..., gt=0,
                          description="Quantity of items")

    @validator('unit_price')
    def validate_unit_price(cls, v):
        if v <= 0:
            raise ValueError('Unit price must be greater than 0')
        if v.as_tuple().exponent < -2:
            raise ValueError('Unit price can have maximum 2 decimal places')
        return v

    @validator('quantity')
    def validate_quantity(cls, v):
        if v <= 0:
            raise ValueError('Quantity must be greater than 0')
        if v > 999:
            raise ValueError('Quantity cannot exceed 999 units')
        return v

    @validator('product_sku')
    def validate_sku(cls, v):
        v = v.upper().strip()
        if not v:
            raise ValueError('Product SKU cannot be empty')
        return v

    @validator('product_name')
    def validate_product_name(cls, v):
        v = v.strip()
        if not v:
            raise ValueError('Product name cannot be empty')
        return v


class CartItemCreate(CartItemBase):
    """Schema para crear un item del carrito"""
    pass


class CartItemUpdate(CamelBaseModel):
    """Schema para actualizar un item del carrito"""
    quantity: Optional[int] = Field(None, gt=0, description="New quantity")

    @validator('quantity')
    def validate_quantity(cls, v):
        if v is not None:
            if v <= 0:
                raise ValueError('Quantity must be greater than 0')
            if v > 999:
                raise ValueError('Quantity cannot exceed 999 units')
        return v


class CartItemResponse(CartItemBase):
    """Schema para respuesta de item del carrito"""
    cart_item_id: UUID
    cart_id: UUID
    subtotal: Decimal
    added_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CartItemListResponse(CamelBaseModel):
    """Schema para lista de items del carrito"""
    cart_items: list[CartItemResponse]
    total: int
