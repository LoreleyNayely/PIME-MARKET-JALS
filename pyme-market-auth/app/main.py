from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.domain.exceptions.status_exception import StatusException
from app.domain.handlers.error_handler import status_exception_handler, exception_handler
from app.api.auth.auth_routes import router as auth_router
from app.core.database_config import engine
from app.infrastructure.db.models.models import Base


@asynccontextmanager
async def lifespan(app_instance: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(
    title="PYME Market Auth API",
    description="Authentication service for PYME Market",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
)

app.add_exception_handler(StatusException, status_exception_handler)
app.add_exception_handler(Exception, exception_handler)
app.include_router(auth_router)
