from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from app.domain.exceptions.status_exception import StatusException
from app.domain.handlers.error_handler import status_exception_handler, exception_handler
from app.api.chat.chat_routes import router as chat_router
from app.core.database_config import engine
from app.infrastructure.db.models.models import Base
from app.infrastructure.websocket.connection_manager import manager
from app.infrastructure.db.models.message_model import MessageModel


@asynccontextmanager
async def lifespan(app_instance: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(
    title="PYME Market Chat API",
    description="Chat microservice with WebSocket support for PYME Market system",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(StatusException, status_exception_handler)
app.add_exception_handler(Exception, exception_handler)
app.include_router(chat_router)


@app.on_event("startup")
async def startup_event():
    asyncio.create_task(manager.start_ping())
