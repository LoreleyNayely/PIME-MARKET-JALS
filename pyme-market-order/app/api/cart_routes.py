from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.dependencies.database import get_db_session
from app.schemas.cart_schema import (
    CartCreate, CartUpdate, CartResponse, CartWithItemsResponse, CartListResponse
)
from app.infrastructure.db.repositories.cart_repository import CartRepository
from app.infrastructure.db.repositories.cart_item_repository import CartItemRepository
from app.domain.services.cart_service import get_cart_service
from app.domain.exceptions.cart_exception import (
    CartNotFoundException, CartAlreadyCompletedException, CartIsEmptyException,
    CartInactiveException, CartAbandonedException, InvalidCartStatusException
)

router = APIRouter(prefix="/carts", tags=["carts"])


@router.post("/", response_model=CartResponse, status_code=status.HTTP_201_CREATED)
async def create_cart(
    cart_data: CartCreate,
    db: AsyncSession = Depends(get_db_session)
):
    """Crear un nuevo carrito"""
    try:
        cart_repository = CartRepository(db)
        cart_item_repository = CartItemRepository(db)
        cart_service = get_cart_service(cart_repository, cart_item_repository)

        cart = await cart_service.create_cart(cart_data)
        return cart

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error creating cart: {str(e)}"
        )


@router.get("/{cart_id}", response_model=CartResponse)
async def get_cart(
    cart_id: UUID,
    db: AsyncSession = Depends(get_db_session)
):
    """Obtener carrito por ID"""
    try:
        cart_repository = CartRepository(db)
        cart_item_repository = CartItemRepository(db)
        cart_service = get_cart_service(cart_repository, cart_item_repository)

        cart = await cart_service.get_cart_by_id(cart_id)
        return cart

    except CartNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.status.description
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/{cart_id}/with-items", response_model=CartWithItemsResponse)
async def get_cart_with_items(
    cart_id: UUID,
    db: AsyncSession = Depends(get_db_session)
):
    """Obtener carrito con sus items incluidos"""
    try:
        cart_repository = CartRepository(db)
        cart_item_repository = CartItemRepository(db)
        cart_service = get_cart_service(cart_repository, cart_item_repository)

        cart = await cart_service.get_cart_with_items(cart_id)
        return cart

    except CartNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.status.description
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/user/{user_id}", response_model=CartListResponse)
async def get_user_carts(
    user_id: str,
    include_inactive: bool = False,
    db: AsyncSession = Depends(get_db_session)
):
    """Obtener todos los carritos de un usuario"""
    try:
        cart_repository = CartRepository(db)
        cart_item_repository = CartItemRepository(db)
        cart_service = get_cart_service(cart_repository, cart_item_repository)

        carts = await cart_service.get_carts_by_user(user_id, include_inactive)
        return CartListResponse(carts=carts, total=len(carts))

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/user/{user_id}/active", response_model=CartResponse)
async def get_or_create_active_cart(
    user_id: str,
    db: AsyncSession = Depends(get_db_session)
):
    """Obtener carrito activo del usuario o crear uno nuevo"""
    try:
        cart_repository = CartRepository(db)
        cart_item_repository = CartItemRepository(db)
        cart_service = get_cart_service(cart_repository, cart_item_repository)

        cart = await cart_service.get_or_create_active_cart(user_id)
        return cart

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.put("/{cart_id}", response_model=CartResponse)
async def update_cart(
    cart_id: UUID,
    update_data: CartUpdate,
    db: AsyncSession = Depends(get_db_session)
):
    """Actualizar un carrito"""
    try:
        cart_repository = CartRepository(db)
        cart_item_repository = CartItemRepository(db)
        cart_service = get_cart_service(cart_repository, cart_item_repository)

        cart = await cart_service.update_cart(cart_id, update_data)
        return cart

    except CartNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.status.description
        )
    except (CartAlreadyCompletedException, CartInactiveException,
            CartAbandonedException, InvalidCartStatusException) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.status.description
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.patch("/{cart_id}/refresh-totals", response_model=CartResponse)
async def refresh_cart_totals(
    cart_id: UUID,
    db: AsyncSession = Depends(get_db_session)
):
    """Recalcular y actualizar totales del carrito"""
    try:
        cart_repository = CartRepository(db)
        cart_item_repository = CartItemRepository(db)
        cart_service = get_cart_service(cart_repository, cart_item_repository)

        cart = await cart_service.refresh_cart_totals(cart_id)
        return cart

    except CartNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.status.description
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.delete("/{cart_id}/clear", response_model=CartResponse)
async def clear_cart(
    cart_id: UUID,
    db: AsyncSession = Depends(get_db_session)
):
    """Vaciar carrito eliminando todos sus items"""
    try:
        cart_repository = CartRepository(db)
        cart_item_repository = CartItemRepository(db)
        cart_service = get_cart_service(cart_repository, cart_item_repository)

        cart = await cart_service.clear_cart(cart_id)
        return cart

    except CartNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.status.description
        )
    except (CartAlreadyCompletedException, CartAbandonedException, CartInactiveException) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.status.description
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.patch("/{cart_id}/complete", response_model=CartResponse)
async def complete_cart(
    cart_id: UUID,
    db: AsyncSession = Depends(get_db_session)
):
    """Marcar carrito como completado"""
    try:
        cart_repository = CartRepository(db)
        cart_item_repository = CartItemRepository(db)
        cart_service = get_cart_service(cart_repository, cart_item_repository)

        cart = await cart_service.complete_cart(cart_id)
        return cart

    except CartNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.status.description
        )
    except (InvalidCartStatusException, CartInactiveException, CartIsEmptyException) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.status.description
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.patch("/{cart_id}/abandon", response_model=CartResponse)
async def abandon_cart(
    cart_id: UUID,
    db: AsyncSession = Depends(get_db_session)
):
    """Marcar carrito como abandonado"""
    try:
        cart_repository = CartRepository(db)
        cart_item_repository = CartItemRepository(db)
        cart_service = get_cart_service(cart_repository, cart_item_repository)

        cart = await cart_service.abandon_cart(cart_id)
        return cart

    except CartNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.status.description
        )
    except CartAlreadyCompletedException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.status.description
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.delete("/{cart_id}")
async def delete_cart(
    cart_id: UUID,
    db: AsyncSession = Depends(get_db_session)
):
    """Eliminar carrito (soft delete)"""
    try:
        cart_repository = CartRepository(db)
        cart_item_repository = CartItemRepository(db)
        cart_service = get_cart_service(cart_repository, cart_item_repository)

        success = await cart_service.delete_cart(cart_id)
        if success:
            return {"message": "Cart deleted successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cart not found"
            )

    except CartNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.status.description
        )
    except CartAlreadyCompletedException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.status.description
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )
