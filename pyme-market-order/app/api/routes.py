from fastapi import FastAPI
from app.api.cart_routes import router as cart_router
from app.api.cart_item_routes import router as cart_item_router
from app.api.purchase_routes import router as purchase_router
from app.api.receipt_routes import router as receipt_router
from app.core.api_config import APIConfig


def register_routes(app: FastAPI) -> None:
    """Registrar todas las rutas de la aplicación"""

    app.include_router(cart_router, prefix=APIConfig.API_VERSION_PREFIX)
    app.include_router(cart_item_router, prefix=APIConfig.API_VERSION_PREFIX)
    app.include_router(purchase_router, prefix=APIConfig.API_VERSION_PREFIX)
    app.include_router(receipt_router, prefix=APIConfig.API_VERSION_PREFIX)


def get_registered_routes() -> dict:
    """Obtener información de todas las rutas registradas"""
    return {
        "cart_routes": {
            "prefix": f"{APIConfig.API_VERSION_PREFIX}/carts",
            "endpoints": [
                "POST /", "GET /{cart_id}", "GET /{cart_id}/with-items",
                "GET /user/{user_id}", "GET /user/{user_id}/active",
                "PUT /{cart_id}", "PATCH /{cart_id}/refresh-totals",
                "DELETE /{cart_id}/clear", "PATCH /{cart_id}/complete",
                "PATCH /{cart_id}/abandon", "DELETE /{cart_id}"
            ]
        },
        "cart_item_routes": {
            "prefix": f"{APIConfig.API_VERSION_PREFIX}/cart-items",
            "endpoints": [
                "POST /{cart_id}/items", "GET /{cart_item_id}",
                "GET /cart/{cart_id}", "PATCH /{cart_item_id}/quantity",
                "PUT /{cart_item_id}", "DELETE /{cart_item_id}",
                "DELETE /cart/{cart_id}/product/{product_id}",
                "DELETE /cart/{cart_id}/clear", "GET /cart/{cart_id}/summary"
            ]
        },
        "purchase_routes": {
            "prefix": f"{APIConfig.API_VERSION_PREFIX}/purchases",
            "endpoints": [
                "POST /", "POST /cart/{cart_id}/process",
                "GET /{purchase_id}", "GET /cart/{cart_id}",
                "GET /number/{purchase_number}", "GET /user/{user_id}",
                "PATCH /{purchase_id}/discount", "PATCH /{purchase_id}/tax",
                "PATCH /{purchase_id}/payment-method", "GET /{purchase_id}/summary"
            ]
        },
        "receipt_routes": {
            "prefix": f"{APIConfig.API_VERSION_PREFIX}/receipts",
            "endpoints": [
                "POST /purchase/{purchase_id}", "GET /{receipt_id}",
                "GET /purchase/{purchase_id}", "GET /purchase/{purchase_id}/get-or-generate",
                "POST /purchase/{purchase_id}/regenerate", "GET /purchase/{purchase_id}/formatted",
                "GET /purchase/{purchase_id}/summary", "DELETE /{receipt_id}"
            ]
        }
    }
