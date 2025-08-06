from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import json
import logging

from app.schemas.chat_schema import MessageCreate, MessageListResponse, WebSocketMessage
from app.domain.services.chat_service import get_chat_service
from app.infrastructure.db.repositories.message_repository import MessageRepository
from app.infrastructure.websocket.connection_manager import manager
from app.api.dependencies.database import get_db_session
from app.core.database_config import AsyncSessionLocal

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/chat", tags=["Chat"])


def get_message_repository(db: AsyncSession = Depends(get_db_session)) -> MessageRepository:
    """Dependency para obtener el repositorio de mensajes"""
    return MessageRepository(db)


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    username: str = Query(..., description="Nombre de usuario"),
    room_id: str = Query("general", description="ID de la sala de chat")
):
    """
    WebSocket endpoint para chat en tiempo real
    """
    await manager.connect(websocket, room_id, username)

    try:
        async with AsyncSessionLocal() as db:
            repository = MessageRepository(db)
            chat_service = get_chat_service(repository, manager)

            recent_messages = await chat_service.get_chat_history(room_id, limit=20)

            history_data = {
                "type": "history",
                "messages": [
                    {
                        "messageId": str(msg.message_id),
                        "content": msg.content,
                        "username": msg.username,
                        "roomId": msg.room_id,
                        "timestamp": msg.timestamp.isoformat()
                    }
                    for msg in recent_messages
                ]
            }
            await manager.send_personal_message(json.dumps(history_data), websocket)

            users_online = await manager.get_room_users(room_id)
            users_data = {
                "type": "users_online",
                "users": users_online
            }
            await manager.send_personal_message(json.dumps(users_data), websocket)

            while True:
                data = await websocket.receive_text()
                message_data = json.loads(data)

                if message_data.get("type") == "message":
                    async with AsyncSessionLocal() as message_db:
                        message_repository = MessageRepository(message_db)
                        message_service = get_chat_service(
                            message_repository, manager)

                        message_create = MessageCreate(
                            content=message_data["content"],
                            username=username,
                            room_id=room_id
                        )

                        await message_service.send_message(message_create)

    except WebSocketDisconnect:
        logger.info(f"Usuario {username} desconectado de la sala {room_id}")
    except Exception as e:
        logger.error(f"Error en WebSocket: {e}")
    finally:
        manager.disconnect(websocket, room_id, username)
        await manager.broadcast_to_room(room_id, {
            "type": "user_left",
            "username": username,
            "message": f"{username} dejó el chat",
            "users_online": await manager.get_room_users(room_id)
        })


@router.get("/history/{room_id}", response_model=MessageListResponse)
async def get_chat_history(
    room_id: str,
    limit: int = Query(
        50, ge=1, le=100, description="Número de mensajes a obtener"),
    repository: MessageRepository = Depends(get_message_repository)
):
    """
    Obtener historial de mensajes de una sala
    """
    try:
        chat_service = get_chat_service(repository, manager)
        messages = await chat_service.get_chat_history(room_id, limit)

        return MessageListResponse(
            messages=messages,
            total=len(messages)
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error obteniendo historial del chat"
        )


@router.get("/rooms/{room_id}/users")
async def get_room_users(room_id: str):
    """
    Obtener usuarios conectados en una sala
    """
    try:
        users = await manager.get_room_users(room_id)
        connection_count = manager.get_room_connection_count(room_id)

        return {
            "room_id": room_id,
            "users_online": users,
            "connection_count": connection_count
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error obteniendo usuarios de la sala"
        )


@router.get("/rooms")
async def get_active_rooms():
    """
    Obtener todas las salas activas
    """
    try:
        rooms = []
        for room_id, connections in manager.active_connections.items():
            if connections:
                rooms.append({
                    "room_id": room_id,
                    "connection_count": len(connections),
                    "users_online": manager.room_users.get(room_id, [])
                })

        return {
            "active_rooms": rooms,
            "total_rooms": len(rooms)
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error obteniendo salas activas"
        )
