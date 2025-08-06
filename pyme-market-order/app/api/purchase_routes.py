from typing import List, Optional
from uuid import UUID
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.dependencies.database import get_db_session
from app.schemas.purchase_schema import (
    PurchaseCreate, PurchaseResponse, PurchaseWithReceiptResponse, PurchaseListResponse
)
from app.infrastructure.db.repositories.purchase_repository import PurchaseRepository
from app.infrastructure.db.repositories.cart_repository import CartRepository
from app.infrastructure.db.repositories.cart_item_repository import CartItemRepository
from app.domain.services.purchase_service import get_purchase_service
from app.domain.exceptions.purchase_exception import (
    PurchaseNotFoundException, PurchaseAlreadyExistsException, InvalidAmountException,
    InvalidDiscountException, InvalidPaymentMethodException, PurchaseProcessingException
)
from app.domain.exceptions.cart_exception import (
    CartNotFoundException, CartIsEmptyException, CartInactiveException, InvalidCartStatusException
)

router = APIRouter(prefix="/purchases", tags=["purchases"])


@router.post("/", response_model=PurchaseResponse, status_code=status.HTTP_201_CREATED)
async def create_purchase(
    purchase_data: PurchaseCreate,
    db: AsyncSession = Depends(get_db_session)
):
    """Crear una nueva compra"""
    try:
        purchase_repository = PurchaseRepository(db)
        cart_repository = CartRepository(db)
        cart_item_repository = CartItemRepository(db)
        purchase_service = get_purchase_service(
            purchase_repository, cart_repository, cart_item_repository)

        purchase = await purchase_service.create_purchase(purchase_data)
        return purchase

    except (CartNotFoundException, CartIsEmptyException, CartInactiveException, InvalidCartStatusException) as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND if isinstance(
                e, CartNotFoundException) else status.HTTP_400_BAD_REQUEST,
            detail=e.status.description
        )
    except PurchaseAlreadyExistsException as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=e.status.description
        )
    except (InvalidAmountException, InvalidDiscountException, InvalidPaymentMethodException) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.status.description
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.post("/cart/{cart_id}/process", response_model=PurchaseResponse, status_code=status.HTTP_201_CREATED)
async def process_cart_purchase(
    cart_id: UUID,
    payment_method: Optional[str] = Query(
        None, description="Payment method: cash, card, transfer"),
    discount_percentage: Optional[float] = Query(
        None, ge=0, le=100, description="Discount percentage (0-100)"),
    tax_percentage: Optional[float] = Query(
        None, ge=0, description="Tax percentage"),
    db: AsyncSession = Depends(get_db_session)
):
    """Procesar compra completa de un carrito"""
    try:
        purchase_repository = PurchaseRepository(db)
        cart_repository = CartRepository(db)
        cart_item_repository = CartItemRepository(db)
        purchase_service = get_purchase_service(
            purchase_repository, cart_repository, cart_item_repository)

        discount_decimal = Decimal(
            str(discount_percentage)) if discount_percentage is not None else None
        tax_decimal = Decimal(
            str(tax_percentage)) if tax_percentage is not None else None

        purchase = await purchase_service.process_cart_purchase(
            cart_id, payment_method, discount_decimal, tax_decimal
        )
        return purchase

    except (CartNotFoundException, CartIsEmptyException, CartInactiveException, InvalidCartStatusException) as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND if isinstance(
                e, CartNotFoundException) else status.HTTP_400_BAD_REQUEST,
            detail=e.status.description
        )
    except PurchaseAlreadyExistsException as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=e.status.description
        )
    except (InvalidAmountException, InvalidDiscountException, InvalidPaymentMethodException) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.status.description
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/{purchase_id}", response_model=PurchaseResponse)
async def get_purchase(
    purchase_id: UUID,
    db: AsyncSession = Depends(get_db_session)
):
    """Obtener compra por ID"""
    try:
        purchase_repository = PurchaseRepository(db)
        cart_repository = CartRepository(db)
        cart_item_repository = CartItemRepository(db)
        purchase_service = get_purchase_service(
            purchase_repository, cart_repository, cart_item_repository)

        purchase = await purchase_service.get_purchase_by_id(purchase_id)
        return purchase

    except PurchaseNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.status.description
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/cart/{cart_id}", response_model=PurchaseResponse)
async def get_purchase_by_cart(
    cart_id: UUID,
    db: AsyncSession = Depends(get_db_session)
):
    """Obtener compra por ID del carrito"""
    try:
        purchase_repository = PurchaseRepository(db)
        cart_repository = CartRepository(db)
        cart_item_repository = CartItemRepository(db)
        purchase_service = get_purchase_service(
            purchase_repository, cart_repository, cart_item_repository)

        purchase = await purchase_service.get_purchase_by_cart_id(cart_id)
        return purchase

    except PurchaseNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.status.description
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/number/{purchase_number}", response_model=PurchaseResponse)
async def get_purchase_by_number(
    purchase_number: str,
    db: AsyncSession = Depends(get_db_session)
):
    """Obtener compra por número"""
    try:
        purchase_repository = PurchaseRepository(db)
        cart_repository = CartRepository(db)
        cart_item_repository = CartItemRepository(db)
        purchase_service = get_purchase_service(
            purchase_repository, cart_repository, cart_item_repository)

        purchase = await purchase_service.get_purchase_by_number(purchase_number)
        return purchase

    except PurchaseNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.status.description
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/user/{user_id}", response_model=PurchaseListResponse)
async def get_user_purchases(
    user_id: str,
    db: AsyncSession = Depends(get_db_session)
):
    """Obtener todas las compras de un usuario"""
    try:
        purchase_repository = PurchaseRepository(db)
        cart_repository = CartRepository(db)
        cart_item_repository = CartItemRepository(db)
        purchase_service = get_purchase_service(
            purchase_repository, cart_repository, cart_item_repository)

        purchases = await purchase_service.get_purchases_by_user(user_id)
        return PurchaseListResponse(purchases=purchases, total=len(purchases))

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.patch("/{purchase_id}/discount", response_model=PurchaseResponse)
async def apply_discount(
    purchase_id: UUID,
    discount_amount: Optional[float] = Query(
        None, ge=0, description="Fixed discount amount"),
    discount_percentage: Optional[float] = Query(
        None, ge=0, le=100, description="Discount percentage (0-100)"),
    db: AsyncSession = Depends(get_db_session)
):
    """Aplicar descuento a una compra"""
    if discount_amount is None and discount_percentage is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either discount_amount or discount_percentage must be provided"
        )

    if discount_amount is not None and discount_percentage is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only one of discount_amount or discount_percentage can be provided"
        )

    try:
        purchase_repository = PurchaseRepository(db)
        cart_repository = CartRepository(db)
        cart_item_repository = CartItemRepository(db)
        purchase_service = get_purchase_service(
            purchase_repository, cart_repository, cart_item_repository)

        discount_amount_decimal = Decimal(
            str(discount_amount)) if discount_amount is not None else None
        discount_percentage_decimal = Decimal(
            str(discount_percentage)) if discount_percentage is not None else None

        purchase = await purchase_service.apply_discount_to_purchase(
            purchase_id, discount_amount_decimal, discount_percentage_decimal
        )
        return purchase

    except PurchaseNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.status.description
        )
    except InvalidDiscountException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.status.description
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.patch("/{purchase_id}/tax", response_model=PurchaseResponse)
async def apply_tax(
    purchase_id: UUID,
    tax_percentage: float = Query(..., ge=0, description="Tax percentage"),
    db: AsyncSession = Depends(get_db_session)
):
    """Aplicar impuesto a una compra"""
    try:
        purchase_repository = PurchaseRepository(db)
        cart_repository = CartRepository(db)
        cart_item_repository = CartItemRepository(db)
        purchase_service = get_purchase_service(
            purchase_repository, cart_repository, cart_item_repository)

        purchase = await purchase_service.apply_tax_to_purchase(purchase_id, Decimal(str(tax_percentage)))
        return purchase

    except PurchaseNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.status.description
        )
    except InvalidAmountException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.status.description
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.patch("/{purchase_id}/payment-method", response_model=PurchaseResponse)
async def update_payment_method(
    purchase_id: UUID,
    payment_method: str = Query(...,
                                description="Payment method: cash, card, transfer"),
    db: AsyncSession = Depends(get_db_session)
):
    """Actualizar método de pago"""
    try:
        purchase_repository = PurchaseRepository(db)
        cart_repository = CartRepository(db)
        cart_item_repository = CartItemRepository(db)
        purchase_service = get_purchase_service(
            purchase_repository, cart_repository, cart_item_repository)

        purchase = await purchase_service.update_payment_method(purchase_id, payment_method)
        return purchase

    except PurchaseNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.status.description
        )
    except InvalidPaymentMethodException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.status.description
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/{purchase_id}/summary")
async def get_purchase_summary(
    purchase_id: UUID,
    db: AsyncSession = Depends(get_db_session)
):
    """Obtener resumen completo de la compra"""
    try:
        purchase_repository = PurchaseRepository(db)
        cart_repository = CartRepository(db)
        cart_item_repository = CartItemRepository(db)
        purchase_service = get_purchase_service(
            purchase_repository, cart_repository, cart_item_repository)

        summary = await purchase_service.get_purchase_summary(purchase_id)
        return summary

    except PurchaseNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.status.description
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )
