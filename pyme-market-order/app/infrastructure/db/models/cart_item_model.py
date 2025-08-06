from sqlalchemy import Column, String, DateTime, Integer, Numeric, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.infrastructure.db.models.models import Base
import uuid
from sqlalchemy.dialects.postgresql import UUID


class CartItemModel(Base):
    __tablename__ = "cart_items"

    cart_item_id = Column(UUID(as_uuid=True), primary_key=True,
                          default=uuid.uuid4, unique=True, nullable=False)
    cart_id = Column(UUID(as_uuid=True), ForeignKey(
        "carts.cart_id"), nullable=False)
    product_id = Column(UUID(as_uuid=True), nullable=False)
    product_name = Column(String(255), nullable=False)
    product_sku = Column(String(100), nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)
    quantity = Column(Integer, nullable=False)
    subtotal = Column(Numeric(10, 2), nullable=False)
    added_at = Column(DateTime(timezone=True),
                      server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(),
                        onupdate=func.now(), nullable=False)

    cart = relationship("CartModel", back_populates="cart_items")
