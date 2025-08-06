from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.domain.entities.message import Message
from app.infrastructure.db.models.message_model import MessageModel
from app.schemas.chat_schema import MessageCreate
from app.domain.exceptions.internal_exception import InternalException


class MessageRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_message(self, message_data: MessageCreate) -> Message:
        """Crear un nuevo mensaje en la base de datos"""
        try:
            message_model = MessageModel(
                content=message_data.content,
                username=message_data.username,
                room_id=message_data.room_id or "general"
            )

            self.session.add(message_model)
            await self.session.commit()
            await self.session.refresh(message_model)

            return self._model_to_entity(message_model)

        except Exception as e:
            await self.session.rollback()
            raise InternalException() from e

    async def get_messages_by_room(self, room_id: str = "general", limit: int = 50) -> List[Message]:
        """Obtener mensajes de una sala específica"""
        try:
            stmt = select(MessageModel).where(
                MessageModel.room_id == room_id
            ).order_by(desc(MessageModel.timestamp)).limit(limit)

            result = await self.session.execute(stmt)
            message_models = result.scalars().all()

            return [self._model_to_entity(model) for model in reversed(message_models)]

        except Exception as e:
            raise InternalException() from e

    async def get_recent_messages(self, room_id: str = "general", limit: int = 20) -> List[Message]:
        """Obtener mensajes recientes para nuevas conexiones"""
        try:
            stmt = select(MessageModel).where(
                MessageModel.room_id == room_id
            ).order_by(desc(MessageModel.timestamp)).limit(limit)

            result = await self.session.execute(stmt)
            message_models = result.scalars().all()

            return [self._model_to_entity(model) for model in reversed(message_models)]

        except Exception as e:
            raise InternalException() from e

    def _model_to_entity(self, message_model: MessageModel) -> Message:
        """Convertir modelo SQLAlchemy a entidad de dominio"""
        return Message(
            message_id=message_model.message_id,
            content=message_model.content,
            username=message_model.username,
            room_id=message_model.room_id,
            timestamp=message_model.timestamp,
            created_at=message_model.created_at
        )
