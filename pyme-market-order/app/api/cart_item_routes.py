from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.dependencies.database import get_db_session
from app.schemas.cart_item_schema import (
    CartItemCreate, CartItemUpdate, CartItemResponse, CartItemListResponse
)
from app.infrastructure.db.repositories.cart_item_repository import CartItemRepository
from app.infrastructure.db.repositories.cart_repository import CartRepository
from app.domain.services.cart_item_service import get_cart_item_service
from app.domain.exceptions.cart_item_exception import (
    CartItemNotFoundException, InvalidQuantityException, ProductAlreadyInCartException,
    InvalidPriceException, ProductDataIncompleteException
)
from app.domain.exceptions.cart_exception import (
    CartNotFoundException, CartInactiveException, CartAlreadyCompletedException
)

router = APIRouter(prefix="/cart-items", tags=["cart-items"])


@router.post("/{cart_id}/items", response_model=CartItemResponse, status_code=status.HTTP_201_CREATED)
async def add_item_to_cart(
    cart_id: UUID,
    item_data: CartItemCreate,
    db: AsyncSession = Depends(get_db_session)
):
    """Agregar item al carrito"""
    try:
        cart_item_repository = CartItemRepository(db)
        cart_repository = CartRepository(db)
        cart_item_service = get_cart_item_service(
            cart_item_repository, cart_repository)

        cart_item = await cart_item_service.add_item_to_cart(cart_id, item_data)
        return cart_item

    except (CartNotFoundException, CartInactiveException, CartAlreadyCompletedException) as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND if isinstance(
                e, CartNotFoundException) else status.HTTP_400_BAD_REQUEST,
            detail=e.status.description
        )
    except (InvalidQuantityException, InvalidPriceException, ProductDataIncompleteException) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.status.description
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/{cart_item_id}", response_model=CartItemResponse)
async def get_cart_item(
    cart_item_id: UUID,
    db: AsyncSession = Depends(get_db_session)
):
    """Obtener item del carrito por ID"""
    try:
        cart_item_repository = CartItemRepository(db)
        cart_repository = CartRepository(db)
        cart_item_service = get_cart_item_service(
            cart_item_repository, cart_repository)

        cart_item = await cart_item_service.get_cart_item_by_id(cart_item_id)
        return cart_item

    except CartItemNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.status.description
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/cart/{cart_id}", response_model=CartItemListResponse)
async def get_cart_items(
    cart_id: UUID,
    db: AsyncSession = Depends(get_db_session)
):
    """Obtener todos los items de un carrito"""
    try:
        cart_item_repository = CartItemRepository(db)
        cart_repository = CartRepository(db)
        cart_item_service = get_cart_item_service(
            cart_item_repository, cart_repository)

        cart_items = await cart_item_service.get_cart_items(cart_id)
        return CartItemListResponse(cart_items=cart_items, total=len(cart_items))

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


@router.patch("/{cart_item_id}/quantity", response_model=CartItemResponse)
async def update_item_quantity(
    cart_item_id: UUID,
    new_quantity: int,
    db: AsyncSession = Depends(get_db_session)
):
    """Actualizar cantidad de un item"""
    try:
        cart_item_repository = CartItemRepository(db)
        cart_repository = CartRepository(db)
        cart_item_service = get_cart_item_service(
            cart_item_repository, cart_repository)

        cart_item = await cart_item_service.update_item_quantity(cart_item_id, new_quantity)
        return cart_item

    except CartItemNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.status.description
        )
    except (CartInactiveException, CartAlreadyCompletedException) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.status.description
        )
    except InvalidQuantityException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.status.description
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.put("/{cart_item_id}", response_model=CartItemResponse)
async def update_cart_item(
    cart_item_id: UUID,
    update_data: CartItemUpdate,
    db: AsyncSession = Depends(get_db_session)
):
    """Actualizar un item del carrito"""
    try:
        cart_item_repository = CartItemRepository(db)
        cart_repository = CartRepository(db)
        cart_item_service = get_cart_item_service(
            cart_item_repository, cart_repository)

        cart_item = await cart_item_service.update_cart_item(cart_item_id, update_data)
        return cart_item

    except CartItemNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.status.description
        )
    except (CartInactiveException, CartAlreadyCompletedException) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.status.description
        )
    except InvalidQuantityException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.status.description
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.delete("/{cart_item_id}")
async def remove_item_from_cart(
    cart_item_id: UUID,
    db: AsyncSession = Depends(get_db_session)
):
    """Eliminar item del carrito"""
    try:
        cart_item_repository = CartItemRepository(db)
        cart_repository = CartRepository(db)
        cart_item_service = get_cart_item_service(
            cart_item_repository, cart_repository)

        success = await cart_item_service.remove_item_from_cart(cart_item_id)
        if success:
            return {"message": "Item removed from cart successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cart item not found"
            )

    except CartItemNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.status.description
        )
    except (CartInactiveException, CartAlreadyCompletedException) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.status.description
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.delete("/cart/{cart_id}/product/{product_id}")
async def remove_product_from_cart(
    cart_id: UUID,
    product_id: UUID,
    db: AsyncSession = Depends(get_db_session)
):
    """Eliminar producto específico del carrito"""
    try:
        cart_item_repository = CartItemRepository(db)
        cart_repository = CartRepository(db)
        cart_item_service = get_cart_item_service(
            cart_item_repository, cart_repository)

        success = await cart_item_service.remove_product_from_cart(cart_id, product_id)
        if success:
            return {"message": "Product removed from cart successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found in cart"
            )

    except CartItemNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.status.description
        )
    except (CartNotFoundException, CartInactiveException, CartAlreadyCompletedException) as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND if isinstance(
                e, CartNotFoundException) else status.HTTP_400_BAD_REQUEST,
            detail=e.status.description
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.delete("/cart/{cart_id}/clear")
async def clear_cart_items(
    cart_id: UUID,
    db: AsyncSession = Depends(get_db_session)
):
    """Eliminar todos los items de un carrito"""
    try:
        cart_item_repository = CartItemRepository(db)
        cart_repository = CartRepository(db)
        cart_item_service = get_cart_item_service(
            cart_item_repository, cart_repository)

        success = await cart_item_service.clear_cart_items(cart_id)
        if success:
            return {"message": "All items removed from cart successfully"}
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
    except (CartInactiveException, CartAlreadyCompletedException) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.status.description
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/cart/{cart_id}/summary")
async def get_cart_summary(
    cart_id: UUID,
    db: AsyncSession = Depends(get_db_session)
):
    """Obtener resumen del carrito"""
    try:
        cart_item_repository = CartItemRepository(db)
        cart_repository = CartRepository(db)
        cart_item_service = get_cart_item_service(
            cart_item_repository, cart_repository)

        summary = await cart_item_service.get_cart_summary(cart_id)
        return summary

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
