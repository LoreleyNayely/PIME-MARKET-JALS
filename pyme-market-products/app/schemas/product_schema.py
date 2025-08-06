from typing import Optional
from datetime import datetime
from decimal import Decimal
from uuid import UUID
from pydantic import Field, validator
from app.core.camel_case_config import CamelBaseModel


class ProductBase(CamelBaseModel):
    """Base schema con campos comunes"""
    name: str = Field(..., min_length=1, max_length=255,
                      description="Product name")
    description: Optional[str] = Field(
        None, max_length=1000, description="Product description")
    price: Decimal = Field(..., gt=0,
                           description="Product price must be greater than 0")
    stock_quantity: int = Field(..., ge=0,
                                description="Stock quantity must be 0 or greater")
    sku: str = Field(..., min_length=1, max_length=100,
                     description="SKU (Stock Keeping Unit)")

    @validator('price')
    def validate_price(cls, v):
        if v <= 0:
            raise ValueError('Price must be greater than 0')
        if v.as_tuple().exponent < -2:
            raise ValueError('Price can have maximum 2 decimal places')
        return v

    @validator('sku')
    def validate_sku(cls, v):
        v = v.upper().strip()
        if not v:
            raise ValueError('SKU cannot be empty')
        return v


class ProductCreate(ProductBase):
    """Schema para crear un producto"""
    pass


class ProductUpdate(CamelBaseModel):
    """Schema para actualizar un producto (campos opcionales)"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    price: Optional[Decimal] = Field(None, gt=0)
    stock_quantity: Optional[int] = Field(None, ge=0)
    sku: Optional[str] = Field(None, min_length=1, max_length=100)
    is_active: Optional[bool] = None

    @validator('price')
    def validate_price(cls, v):
        if v is not None and v <= 0:
            raise ValueError('Price must be greater than 0')
        if v is not None and v.as_tuple().exponent < -2:
            raise ValueError('Price can have maximum 2 decimal places')
        return v

    @validator('sku')
    def validate_sku(cls, v):
        if v is not None:
            v = v.upper().strip()
            if not v:
                raise ValueError('SKU cannot be empty')
        return v


class ProductResponse(ProductBase):
    """Schema para respuesta de producto"""
    product_id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProductListResponse(CamelBaseModel):
    """Schema para lista de productos"""
    products: list[ProductResponse]
    total: int
