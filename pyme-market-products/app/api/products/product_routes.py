from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.product_schema import (
    ProductCreate,
    ProductUpdate,
    ProductResponse,
    ProductListResponse
)
from app.domain.services.product_service import get_product_service
from app.infrastructure.db.repositories.product_repository import ProductRepository
from app.api.dependencies.database import get_db_session
from app.domain.exceptions.product_exception import (
    ProductNotFoundException,
    DuplicateSkuException,
    InvalidStockException,
    InvalidPriceException,
    ProductInactiveException
)

router = APIRouter(prefix="/products", tags=["Products"])


def get_product_repository(db: AsyncSession = Depends(get_db_session)) -> ProductRepository:
    """Dependency para obtener el repositorio de productos"""
    return ProductRepository(db)


@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    product_data: ProductCreate,
    repository: ProductRepository = Depends(get_product_repository)
):
    """
    Crear un nuevo producto
    """
    try:
        service = get_product_service(repository)
        product = await service.create_product(product_data)
        return product

    except DuplicateSkuException as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=e.status.description
        )
    except (InvalidPriceException, InvalidStockException) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.status.description
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while creating product"
        )


@router.get("/", response_model=ProductListResponse)
async def get_all_products(
    include_inactive: bool = Query(
        False, description="Include inactive products"),
    repository: ProductRepository = Depends(get_product_repository)
):
    """
    Obtener todos los productos
    """
    try:
        service = get_product_service(repository)
        products = await service.get_all_products(include_inactive)

        return ProductListResponse(
            products=products,
            total=len(products)
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while fetching products"
        )


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product_by_id(
    product_id: UUID,
    repository: ProductRepository = Depends(get_product_repository)
):
    """
    Obtener un producto por su ID
    """
    try:
        service = get_product_service(repository)
        product = await service.get_product_by_id(product_id)
        return product

    except ProductNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.status.description
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while fetching product"
        )


@router.get("/sku/{sku}", response_model=ProductResponse)
async def get_product_by_sku(
    sku: str,
    repository: ProductRepository = Depends(get_product_repository)
):
    """
    Obtener un producto por su SKU
    """
    try:
        service = get_product_service(repository)
        product = await service.get_product_by_sku(sku)
        return product

    except ProductNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.status.description
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while fetching product"
        )


@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: UUID,
    update_data: ProductUpdate,
    repository: ProductRepository = Depends(get_product_repository)
):
    """
    Actualizar un producto completamente
    """
    try:
        service = get_product_service(repository)
        product = await service.update_product(product_id, update_data)
        return product

    except ProductNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.status.description
        )
    except DuplicateSkuException as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=e.status.description
        )
    except (InvalidPriceException, InvalidStockException) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.status.description
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while updating product"
        )


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: UUID,
    repository: ProductRepository = Depends(get_product_repository)
):
    """
    Eliminar un producto (soft delete)
    """
    try:
        service = get_product_service(repository)
        await service.delete_product(product_id)

    except ProductNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.status.description
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while deleting product"
        )


@router.patch("/{product_id}/restore", response_model=ProductResponse)
async def restore_product(
    product_id: UUID,
    repository: ProductRepository = Depends(get_product_repository)
):
    """
    Restaurar un producto eliminado
    """
    try:
        service = get_product_service(repository)
        await service.restore_product(product_id)
        product = await service.get_product_by_id(product_id)
        return product

    except ProductNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.status.description
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while restoring product"
        )


@router.patch("/{product_id}/stock", response_model=ProductResponse)
async def update_product_stock(
    product_id: UUID,
    new_stock: int = Query(..., ge=0, description="New stock quantity"),
    repository: ProductRepository = Depends(get_product_repository)
):
    """
    Actualizar solo el stock de un producto
    """
    try:
        service = get_product_service(repository)
        product = await service.update_stock(product_id, new_stock)
        return product

    except ProductNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.status.description
        )
    except (ProductInactiveException, InvalidStockException) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.status.description
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while updating stock"
        )


@router.patch("/{product_id}/stock/reduce", response_model=ProductResponse)
async def reduce_product_stock(
    product_id: UUID,
    quantity: int = Query(..., gt=0, description="Quantity to reduce"),
    repository: ProductRepository = Depends(get_product_repository)
):
    """
    Reducir stock de un producto (para ventas)
    """
    try:
        service = get_product_service(repository)
        product = await service.reduce_stock(product_id, quantity)
        return product

    except ProductNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.status.description
        )
    except (ProductInactiveException, InvalidStockException) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.status.description
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while reducing stock"
        )


@router.patch("/{product_id}/stock/increase", response_model=ProductResponse)
async def increase_product_stock(
    product_id: UUID,
    quantity: int = Query(..., gt=0, description="Quantity to add"),
    repository: ProductRepository = Depends(get_product_repository)
):
    """
    Aumentar stock de un producto (para reposiciones)
    """
    try:
        service = get_product_service(repository)
        product = await service.increase_stock(product_id, quantity)
        return product

    except ProductNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.status.description
        )
    except (ProductInactiveException, InvalidStockException) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.status.description
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while increasing stock"
        )


@router.get("/{product_id}/stock/check", response_model=dict)
async def check_stock_availability(
    product_id: UUID,
    required_quantity: int = Query(..., gt=0,
                                   description="Required quantity to check"),
    repository: ProductRepository = Depends(get_product_repository)
):
    """
    Verificar si hay suficiente stock disponible
    """
    try:
        service = get_product_service(repository)
        is_available = await service.check_stock_availability(product_id, required_quantity)

        product = await service.get_product_by_id(product_id)

        return {
            "product_id": str(product_id),
            "sku": product.sku,
            "current_stock": product.stock_quantity,
            "required_quantity": required_quantity,
            "is_available": is_available,
            "available_quantity": product.stock_quantity if is_available else 0
        }

    except ProductNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.status.description
        )
    except ProductInactiveException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.status.description
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while checking stock"
        )
