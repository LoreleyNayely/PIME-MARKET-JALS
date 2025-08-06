from typing import Optional, List, TYPE_CHECKING
from datetime import datetime
from decimal import Decimal
from uuid import UUID
from pydantic import Field, validator
from app.core.camel_case_config import CamelBaseModel


class CartBase(CamelBaseModel):
    """Base schema con campos comunes del carrito"""
    user_id: str = Field(..., min_length=1, max_length=255,
                         description="User ID who owns the cart")
    status: str = Field(
        default="active", description="Cart status: active, completed, abandoned")

    @validator('status')
    def validate_status(cls, v):
        allowed_statuses = ['active', 'completed', 'abandoned']
        if v not in allowed_statuses:
            raise ValueError(
                f'Status must be one of: {", ".join(allowed_statuses)}')
        return v

    @validator('user_id')
    def validate_user_id(cls, v):
        v = v.strip()
        if not v:
            raise ValueError('User ID cannot be empty')
        return v


class CartCreate(CartBase):
    """Schema para crear un carrito"""
    pass


class CartUpdate(CamelBaseModel):
    """Schema para actualizar un carrito (campos opcionales)"""
    status: Optional[str] = None

    @validator('status')
    def validate_status(cls, v):
        if v is not None:
            allowed_statuses = ['active', 'completed', 'abandoned']
            if v not in allowed_statuses:
                raise ValueError(
                    f'Status must be one of: {", ".join(allowed_statuses)}')
        return v


class CartResponse(CartBase):
    """Schema para respuesta de carrito"""
    cart_id: UUID
    total_amount: Decimal
    total_items: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CartWithItemsResponse(CartResponse):
    """Schema para carrito con sus items"""
    cart_items: List['CartItemResponse'] = []

    class Config:
        from_attributes = True


class CartListResponse(CamelBaseModel):
    """Schema para lista de carritos"""
    carts: List[CartResponse]
    total: int
