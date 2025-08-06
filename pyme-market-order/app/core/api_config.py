from typing import Dict, Any


class APIConfig:
    """Configuración de la API"""

    TITLE = "PYME Market Order Management API"
    DESCRIPTION = "API for managing shopping carts, purchases, and receipts in PYME Market system"
    VERSION = "1.0.0"

    API_VERSION_PREFIX = "/api/v1"
    DOCS_URL = "/docs"
    REDOC_URL = "/redoc"
    OPENAPI_URL = "/openapi.json"

    TAGS_METADATA = [
        {
            "name": "carts",
            "description": "Operations with shopping carts. Create, read, update and manage cart states.",
        },
        {
            "name": "cart-items",
            "description": "Operations with cart items. Add, remove, and update products in carts.",
        },
        {
            "name": "purchases",
            "description": "Operations with purchases. Process cart purchases, apply discounts and taxes.",
        },
        {
            "name": "receipts",
            "description": "Operations with receipts. Generate and manage purchase receipts.",
        },
    ]

    @classmethod
    def get_fastapi_config(cls) -> Dict[str, Any]:
        """Obtener configuración para FastAPI"""
        return {
            "title": cls.TITLE,
            "description": cls.DESCRIPTION,
            "version": cls.VERSION,
            "docs_url": cls.DOCS_URL,
            "redoc_url": cls.REDOC_URL,
            "openapi_url": cls.OPENAPI_URL,
            "openapi_tags": cls.TAGS_METADATA,
        }

    @classmethod
    def get_endpoints_info(cls) -> Dict[str, str]:
        """Obtener información de endpoints"""
        return {
            "carts": f"{cls.API_VERSION_PREFIX}/carts",
            "cart_items": f"{cls.API_VERSION_PREFIX}/cart-items",
            "purchases": f"{cls.API_VERSION_PREFIX}/purchases",
            "receipts": f"{cls.API_VERSION_PREFIX}/receipts"
        }
