from typing import Optional
from datetime import datetime
from uuid import UUID
from app.core.camel_case_config import CamelBaseModel


class Message(CamelBaseModel):
    message_id: Optional[UUID] = None
    content: str
    username: str
    room_id: Optional[str] = "general"
    timestamp: Optional[datetime] = None
    created_at: Optional[datetime] = None
