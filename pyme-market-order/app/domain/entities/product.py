from typing import Optional
from datetime import datetime
from decimal import Decimal
from uuid import UUID
from app.core.camel_case_config import CamelBaseModel


class Product(CamelBaseModel):
    product_id: Optional[UUID] = None
    name: str
    description: Optional[str] = None
    price: Decimal
    stock_quantity: int
    sku: str
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
