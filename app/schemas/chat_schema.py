from app.core.camel_case_config import CamelBaseModel
from pydantic import Field
from typing import Optional
from uuid import UUID
from datetime import datetime


class MessageBase(CamelBaseModel):
    content: str = Field(..., min_length=1, max_length=1000,
                         description="Message content")
    username: str = Field(..., min_length=1, max_length=50,
                          description="Username")
    room_id: Optional[str] = Field(
        "general", max_length=50, description="Chat room ID")


class MessageCreate(MessageBase):
    pass


class MessageResponse(MessageBase):
    message_id: UUID
    timestamp: datetime
    created_at: datetime

    class Config:
        from_attributes = True


class MessageListResponse(CamelBaseModel):
    messages: list[MessageResponse]
    total: int


class WebSocketMessage(CamelBaseModel):
    type: str
    content: str
    username: str
    room_id: Optional[str] = "general"
    timestamp: Optional[datetime] = None
