from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.domain.exceptions.status_exception import StatusException
from app.domain.handlers.error_handler import status_exception_handler, exception_handler
from app.api.products.product_routes import router as products_router
from app.core.database_config import engine
from app.infrastructure.db.models.models import Base
from app.infrastructure.db.models.product_model import ProductModel


@asynccontextmanager
async def lifespan(app_instance: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(
    title="PYME Market Products API",
    description="API for managing products in PYME Market system",
    version="1.0.0",
    lifespan=lifespan,
    root_path="/api/v1"
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
app.include_router(products_router)
