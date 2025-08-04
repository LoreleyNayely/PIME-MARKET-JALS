from typing import List
from datetime import datetime
from app.domain.entities.message import Message
from app.schemas.chat_schema import MessageCreate, WebSocketMessage
from app.infrastructure.db.repositories.message_repository import MessageRepository
from app.infrastructure.websocket.connection_manager import ConnectionManager


class ChatService:
    def __init__(self, message_repository: MessageRepository, connection_manager: ConnectionManager):
        self.message_repository = message_repository
        self.connection_manager = connection_manager

    async def send_message(self, message_data: MessageCreate) -> Message:
        """Procesar y persistir un mensaje del chat"""
        self._validate_message_content(message_data.content)
        self._validate_username(message_data.username)

        message = await self.message_repository.create_message(message_data)

        ws_message = {
            "type": "message",
            "messageId": str(message.message_id),
            "content": message.content,
            "username": message.username,
            "roomId": message.room_id,
            "timestamp": message.timestamp.isoformat()
        }

        await self.connection_manager.broadcast_to_room(
            message.room_id,
            ws_message
        )

        return message

    async def get_chat_history(self, room_id: str = "general", limit: int = 20) -> List[Message]:
        """Obtener historial de mensajes para una sala"""
        return await self.message_repository.get_recent_messages(room_id, limit)

    async def handle_user_join(self, username: str, room_id: str = "general") -> List[Message]:
        """Manejar cuando un usuario se une al chat"""
        recent_messages = await self.get_chat_history(room_id, limit=20)

        users_online = await self.connection_manager.get_room_users(room_id)

        return recent_messages

    async def handle_user_leave(self, username: str, room_id: str = "general"):
        """Manejar cuando un usuario deja el chat"""
        await self.connection_manager.broadcast_to_room(room_id, {
            "type": "user_left",
            "username": username,
            "message": f"{username} dejó el chat",
            "users_online": await self.connection_manager.get_room_users(room_id)
        })

    def _validate_message_content(self, content: str) -> None:
        """Validar contenido del mensaje"""
        if not content or not content.strip():
            raise ValueError("El mensaje no puede estar vacío")

        if len(content) > 1000:
            raise ValueError(
                "El mensaje es demasiado largo (máximo 1000 caracteres)")

    def _validate_username(self, username: str) -> None:
        """Validar nombre de usuario"""
        if not username or not username.strip():
            raise ValueError("El nombre de usuario no puede estar vacío")

        if len(username) > 50:
            raise ValueError(
                "El nombre de usuario es demasiado largo (máximo 50 caracteres)")


def get_chat_service(message_repository: MessageRepository, connection_manager: ConnectionManager) -> ChatService:
    """Factory function para obtener instancia del servicio de chat"""
    return ChatService(message_repository, connection_manager)
