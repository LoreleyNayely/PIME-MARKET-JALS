from sqlalchemy import Column, String, DateTime, Numeric, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.infrastructure.db.models.models import Base
import uuid
from sqlalchemy.dialects.postgresql import UUID


class PurchaseModel(Base):
    __tablename__ = "purchases"

    purchase_id = Column(UUID(as_uuid=True), primary_key=True,
                         default=uuid.uuid4, unique=True, nullable=False)
    cart_id = Column(UUID(as_uuid=True), ForeignKey(
        "carts.cart_id"), nullable=False)
    user_id = Column(String(255), nullable=False)
    purchase_number = Column(String(100), unique=True, nullable=False)
    total_amount = Column(Numeric(10, 2), nullable=False)
    tax_amount = Column(Numeric(10, 2), default=0.00, nullable=False)
    discount_amount = Column(Numeric(10, 2), default=0.00, nullable=False)
    final_amount = Column(Numeric(10, 2), nullable=False)
    payment_method = Column(String(50), nullable=True)
    status = Column(String(50), default="completed", nullable=False)
    purchased_at = Column(DateTime(timezone=True),
                          server_default=func.now(), nullable=False)

    cart = relationship("CartModel", back_populates="purchase")
    receipt = relationship(
        "ReceiptModel", back_populates="purchase", uselist=False)
