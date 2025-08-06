from typing import Dict, List, Set
from fastapi import WebSocket
import json
import logging
import asyncio
from datetime import datetime

logger = logging.getLogger(__name__)


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        self.room_users: Dict[str, Dict[str, Set[WebSocket]]] = {}
        self.last_ping: Dict[WebSocket, datetime] = {}

    async def connect(self, websocket: WebSocket, room_id: str = "general", username: str = "Anonymous"):
        """Aceptar nueva conexión WebSocket"""
        try:
            await websocket.accept()

            if room_id not in self.active_connections:
                self.active_connections[room_id] = set()
                self.room_users[room_id] = {}

            if username not in self.room_users[room_id]:
                self.room_users[room_id][username] = set()

            self.active_connections[room_id].add(websocket)
            self.room_users[room_id][username].add(websocket)
            self.last_ping[websocket] = datetime.now()

            logger.info(f"Usuario {username} conectado a la sala {room_id}")

            await self.broadcast_to_room(room_id, {
                "type": "user_joined",
                "username": username,
                "message": f"{username} se unió al chat",
                "users_online": await self.get_room_users(room_id)
            }, exclude_websocket=websocket)

        except Exception as e:
            logger.error(f"Error en connect: {e}")
            raise

    def disconnect(self, websocket: WebSocket, room_id: str = "general", username: str = "Anonymous"):
        """Remover conexión WebSocket"""
        try:
            if room_id in self.active_connections:
                self.active_connections[room_id].discard(websocket)

            if room_id in self.room_users and username in self.room_users[room_id]:
                self.room_users[room_id][username].discard(websocket)
                if not self.room_users[room_id][username]:
                    del self.room_users[room_id][username]

            self.last_ping.pop(websocket, None)

            logger.info(
                f"Usuario {username} desconectado de la sala {room_id}")

        except Exception as e:
            logger.error(f"Error en disconnect: {e}")

    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Enviar mensaje a una conexión específica"""
        try:
            await websocket.send_text(message)
        except Exception as e:
            logger.error(f"Error enviando mensaje personal: {e}")
            await self.handle_broken_connection(websocket)

    async def broadcast_to_room(self, room_id: str, message: dict, exclude_websocket: WebSocket = None):
        """Enviar mensaje a todas las conexiones de una sala"""
        if room_id not in self.active_connections:
            return

        message_text = json.dumps(message)
        broken_connections = set()

        for websocket in self.active_connections[room_id]:
            if exclude_websocket and websocket == exclude_websocket:
                continue

            try:
                await websocket.send_text(message_text)
            except Exception as e:
                logger.error(f"Error enviando mensaje a WebSocket: {e}")
                broken_connections.add(websocket)

        for ws in broken_connections:
            await self.handle_broken_connection(ws)

    async def get_room_users(self, room_id: str) -> List[str]:
        """Obtener lista de usuarios conectados en una sala"""
        if room_id not in self.room_users:
            return []
        return list(self.room_users[room_id].keys())

    def get_room_connection_count(self, room_id: str) -> int:
        """Obtener número de conexiones activas en una sala"""
        return len(self.active_connections.get(room_id, set()))

    async def handle_broken_connection(self, websocket: WebSocket):
        """Manejar una conexión rota"""
        room_id = None
        username = None

        for rid, connections in self.active_connections.items():
            if websocket in connections:
                room_id = rid
                for uname, user_connections in self.room_users[rid].items():
                    if websocket in user_connections:
                        username = uname
                        break
                break

        if room_id and username:
            self.disconnect(websocket, room_id, username)

    async def start_ping(self):
        """Iniciar el ping periódico para mantener las conexiones vivas"""
        while True:
            await asyncio.sleep(30)
            await self.ping_all_connections()

    async def ping_all_connections(self):
        """Enviar ping a todas las conexiones activas"""
        broken_connections = set()
        current_time = datetime.now()

        for room_connections in self.active_connections.values():
            for websocket in room_connections:
                try:
                    await websocket.send_text(json.dumps({"type": "ping"}))
                    self.last_ping[websocket] = current_time
                except Exception as e:
                    logger.error(f"Error enviando ping: {e}")
                    broken_connections.add(websocket)

        for ws in broken_connections:
            await self.handle_broken_connection(ws)


manager = ConnectionManager()
