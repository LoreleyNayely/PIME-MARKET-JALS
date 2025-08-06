from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.domain.exceptions.status_exception import StatusException
from app.domain.handlers.error_handler import status_exception_handler, exception_handler
from app.core.database_config import engine
from app.core.api_config import APIConfig
from app.api.routes import register_routes, get_registered_routes
from app.infrastructure.db.models.models import Base
from app.infrastructure.db.models import (
    product_model, cart_model, cart_item_model, purchase_model, receipt_model
)


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Gestionar el ciclo de vida de la aplicación"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(
    lifespan=lifespan,
    **APIConfig.get_fastapi_config()
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(StatusException, status_exception_handler)
app.add_exception_handler(Exception, exception_handler)

register_routes(app)


@app.get("/")
async def root():
    """Endpoint raíz con información de la API"""
    return {
        "message": APIConfig.TITLE,
        "version": APIConfig.VERSION,
        "description": APIConfig.DESCRIPTION,
        "docs": APIConfig.DOCS_URL,
        "redoc": APIConfig.REDOC_URL,
        "endpoints": APIConfig.get_endpoints_info()
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "pyme-market-order",
        "version": APIConfig.VERSION
    }


@app.get("/routes")
async def get_routes():
    """Endpoint para obtener información detallada de todas las rutas"""
    return {
        "api_version": APIConfig.API_VERSION_PREFIX,
        "total_route_groups": 4,
        "routes": get_registered_routes()
    }
