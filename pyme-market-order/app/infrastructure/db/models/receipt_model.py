from sqlalchemy import Column, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, JSON
from app.infrastructure.db.models.models import Base
import uuid


class ReceiptModel(Base):
    __tablename__ = "receipts"

    receipt_id = Column(UUID(as_uuid=True), primary_key=True,
                        default=uuid.uuid4, unique=True, nullable=False)
    purchase_id = Column(UUID(as_uuid=True), ForeignKey(
        "purchases.purchase_id"), nullable=False)
    receipt_data = Column(JSON, nullable=False)
    generated_at = Column(DateTime(timezone=True),
                          server_default=func.now(), nullable=False)

    purchase = relationship("PurchaseModel", back_populates="receipt")

    __table_args__ = (
        UniqueConstraint('purchase_id', name='uq_receipt_purchase_id'),
    )
