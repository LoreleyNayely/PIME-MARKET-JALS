from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.sql import func
from app.infrastructure.db.models.models import Base
import uuid
from sqlalchemy.dialects.postgresql import UUID


class UserModel(Base):
    __tablename__ = "users"

    user_id = Column(UUID(as_uuid=True), primary_key=True,
                     default=uuid.uuid4, unique=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    is_reset_password = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True),
                        server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(),
                        onupdate=func.now(), nullable=False)
