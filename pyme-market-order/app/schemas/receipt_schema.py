from datetime import datetime
from uuid import UUID
from typing import Dict, Any
from app.core.camel_case_config import CamelBaseModel


class ReceiptResponse(CamelBaseModel):
    """Schema para respuesta de recibo"""
    receipt_id: UUID
    purchase_id: UUID
    receipt_data: Dict[str, Any]
    generated_at: datetime

    class Config:
        from_attributes = True


class ReceiptDataSchema(CamelBaseModel):
    """Schema para el contenido del JSON del recibo"""
    purchase_number: str
    user_id: str
    purchase_date: datetime
    total_amount: float
    tax_amount: float
    discount_amount: float
    final_amount: float
    payment_method: str
    items: list[Dict[str, Any]]
    summary: Dict[str, Any]
