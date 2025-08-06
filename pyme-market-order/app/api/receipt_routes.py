from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import PlainTextResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.dependencies.database import get_db_session
from app.schemas.receipt_schema import ReceiptResponse
from app.infrastructure.db.repositories.receipt_repository import ReceiptRepository
from app.infrastructure.db.repositories.purchase_repository import PurchaseRepository
from app.infrastructure.db.repositories.cart_item_repository import CartItemRepository
from app.domain.services.receipt_service import get_receipt_service
from app.domain.exceptions.receipt_exception import (
    ReceiptNotFoundException, ReceiptAlreadyExistsException, ReceiptGenerationException,
    InvalidReceiptDataException
)
from app.domain.exceptions.purchase_exception import PurchaseNotFoundException

router = APIRouter(prefix="/receipts", tags=["receipts"])


@router.post("/purchase/{purchase_id}", response_model=ReceiptResponse, status_code=status.HTTP_201_CREATED)
async def generate_receipt(
    purchase_id: UUID,
    db: AsyncSession = Depends(get_db_session)
):
    """Generar recibo para una compra"""
    try:
        receipt_repository = ReceiptRepository(db)
        purchase_repository = PurchaseRepository(db)
        cart_item_repository = CartItemRepository(db)
        receipt_service = get_receipt_service(
            receipt_repository, purchase_repository, cart_item_repository)

        receipt = await receipt_service.generate_receipt(purchase_id)
        return receipt

    except PurchaseNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.status.description
        )
    except ReceiptAlreadyExistsException as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=e.status.description
        )
    except ReceiptGenerationException as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=e.status.description
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/{receipt_id}", response_model=ReceiptResponse)
async def get_receipt(
    receipt_id: UUID,
    db: AsyncSession = Depends(get_db_session)
):
    """Obtener recibo por ID"""
    try:
        receipt_repository = ReceiptRepository(db)
        purchase_repository = PurchaseRepository(db)
        cart_item_repository = CartItemRepository(db)
        receipt_service = get_receipt_service(
            receipt_repository, purchase_repository, cart_item_repository)

        receipt = await receipt_service.get_receipt_by_id(receipt_id)
        return receipt

    except ReceiptNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.status.description
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/purchase/{purchase_id}", response_model=ReceiptResponse)
async def get_receipt_by_purchase(
    purchase_id: UUID,
    db: AsyncSession = Depends(get_db_session)
):
    """Obtener recibo por ID de compra"""
    try:
        receipt_repository = ReceiptRepository(db)
        purchase_repository = PurchaseRepository(db)
        cart_item_repository = CartItemRepository(db)
        receipt_service = get_receipt_service(
            receipt_repository, purchase_repository, cart_item_repository)

        receipt = await receipt_service.get_receipt_by_purchase_id(purchase_id)
        return receipt

    except ReceiptNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.status.description
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/purchase/{purchase_id}/get-or-generate", response_model=ReceiptResponse)
async def get_or_generate_receipt(
    purchase_id: UUID,
    db: AsyncSession = Depends(get_db_session)
):
    """Obtener recibo existente o generar uno nuevo"""
    try:
        receipt_repository = ReceiptRepository(db)
        purchase_repository = PurchaseRepository(db)
        cart_item_repository = CartItemRepository(db)
        receipt_service = get_receipt_service(
            receipt_repository, purchase_repository, cart_item_repository)

        receipt = await receipt_service.get_or_generate_receipt(purchase_id)
        return receipt

    except PurchaseNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.status.description
        )
    except ReceiptGenerationException as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=e.status.description
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.post("/purchase/{purchase_id}/regenerate", response_model=ReceiptResponse)
async def regenerate_receipt(
    purchase_id: UUID,
    db: AsyncSession = Depends(get_db_session)
):
    """Regenerar recibo para una compra"""
    try:
        receipt_repository = ReceiptRepository(db)
        purchase_repository = PurchaseRepository(db)
        cart_item_repository = CartItemRepository(db)
        receipt_service = get_receipt_service(
            receipt_repository, purchase_repository, cart_item_repository)

        receipt = await receipt_service.regenerate_receipt(purchase_id)
        return receipt

    except PurchaseNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.status.description
        )
    except ReceiptGenerationException as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=e.status.description
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/purchase/{purchase_id}/formatted", response_class=PlainTextResponse)
async def get_formatted_receipt(
    purchase_id: UUID,
    db: AsyncSession = Depends(get_db_session)
):
    """Obtener recibo formateado como texto para impresión"""
    try:
        receipt_repository = ReceiptRepository(db)
        purchase_repository = PurchaseRepository(db)
        cart_item_repository = CartItemRepository(db)
        receipt_service = get_receipt_service(
            receipt_repository, purchase_repository, cart_item_repository)

        formatted_receipt = await receipt_service.get_formatted_receipt(purchase_id)
        return formatted_receipt

    except ReceiptNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.status.description
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/purchase/{purchase_id}/summary")
async def get_receipt_summary(
    purchase_id: UUID,
    db: AsyncSession = Depends(get_db_session)
):
    """Obtener resumen del recibo"""
    try:
        receipt_repository = ReceiptRepository(db)
        purchase_repository = PurchaseRepository(db)
        cart_item_repository = CartItemRepository(db)
        receipt_service = get_receipt_service(
            receipt_repository, purchase_repository, cart_item_repository)

        summary = await receipt_service.get_receipt_summary(purchase_id)
        return summary

    except ReceiptNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.status.description
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.delete("/{receipt_id}")
async def delete_receipt(
    receipt_id: UUID,
    db: AsyncSession = Depends(get_db_session)
):
    """Eliminar un recibo"""
    try:
        receipt_repository = ReceiptRepository(db)
        purchase_repository = PurchaseRepository(db)
        cart_item_repository = CartItemRepository(db)
        receipt_service = get_receipt_service(
            receipt_repository, purchase_repository, cart_item_repository)

        success = await receipt_service.delete_receipt(receipt_id)
        if success:
            return {"message": "Receipt deleted successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Receipt not found"
            )

    except ReceiptNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.status.description
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )
