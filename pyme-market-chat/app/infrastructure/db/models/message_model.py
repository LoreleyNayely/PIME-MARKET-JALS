from sqlalchemy import Column, String, DateTime, Text
from sqlalchemy.sql import func
from app.infrastructure.db.models.models import Base
import uuid
from sqlalchemy.dialects.postgresql import UUID


class MessageModel(Base):
    __tablename__ = "messages"

    message_id = Column(UUID(as_uuid=True), primary_key=True,
                        default=uuid.uuid4, unique=True, nullable=False)
    content = Column(Text, nullable=False)
    username = Column(String(50), nullable=False)
    room_id = Column(String(50), default="general", nullable=False)
    timestamp = Column(DateTime(timezone=True),
                       server_default=func.now(), nullable=False)
    created_at = Column(DateTime(timezone=True),
                        server_default=func.now(), nullable=False)
