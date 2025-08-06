from sqlalchemy import Column, String, Boolean, DateTime, Integer, Numeric
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.infrastructure.db.models.models import Base
import uuid
from sqlalchemy.dialects.postgresql import UUID


class CartModel(Base):
    __tablename__ = "carts"

    cart_id = Column(UUID(as_uuid=True), primary_key=True,
                     default=uuid.uuid4, unique=True, nullable=False)
    user_id = Column(String(255), nullable=False, index=True)
    status = Column(String(50), default="active", nullable=False)
    total_amount = Column(Numeric(10, 2), default=0.00, nullable=False)
    total_items = Column(Integer, default=0, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True),
                        server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(),
                        onupdate=func.now(), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    cart_items = relationship(
        "CartItemModel", back_populates="cart", cascade="all, delete-orphan")
    purchase = relationship(
        "PurchaseModel", back_populates="cart", uselist=False)
