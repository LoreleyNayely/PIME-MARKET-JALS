from typing import Optional, List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from app.domain.entities.receipt import Receipt
from app.infrastructure.db.models.receipt_model import ReceiptModel
from app.domain.exceptions.not_found_exception import NotFoundException
from app.domain.exceptions.internal_exception import InternalException


class ReceiptRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_receipt(self, purchase_id: UUID, receipt_data: dict) -> Receipt:
        """Crear un nuevo recibo"""
        try:
            receipt_model = ReceiptModel(
                purchase_id=purchase_id,
                receipt_data=receipt_data
            )

            self.session.add(receipt_model)
            await self.session.commit()
            await self.session.refresh(receipt_model)

            return self._model_to_entity(receipt_model)

        except IntegrityError as e:
            await self.session.rollback()
            if 'uq_receipt_purchase_id' in str(e):
                return await self.get_receipt_by_purchase_id(purchase_id)
            raise InternalException() from e
        except Exception as e:
            await self.session.rollback()
            raise InternalException() from e

    async def get_receipt_by_id(self, receipt_id: UUID) -> Optional[Receipt]:
        """Obtener recibo por ID"""
        try:
            stmt = select(ReceiptModel).where(
                ReceiptModel.receipt_id == receipt_id)
            result = await self.session.execute(stmt)
            receipt_model = result.scalar_one_or_none()

            if receipt_model:
                return self._model_to_entity(receipt_model)
            return None

        except Exception as e:
            raise InternalException() from e

    async def get_receipt_by_purchase_id(self, purchase_id: UUID) -> Optional[Receipt]:
        """Obtener recibo por ID de compra"""
        try:
            stmt = select(ReceiptModel).where(
                ReceiptModel.purchase_id == purchase_id)
            result = await self.session.execute(stmt)
            receipt_model = result.scalar_one_or_none()

            if receipt_model:
                return self._model_to_entity(receipt_model)
            return None

        except Exception as e:
            raise InternalException() from e

    async def update_receipt_data(self, receipt_id: UUID, receipt_data: dict) -> Receipt:
        """Actualizar datos del recibo"""
        try:
            stmt = select(ReceiptModel).where(
                ReceiptModel.receipt_id == receipt_id)
            result = await self.session.execute(stmt)
            receipt_model = result.scalar_one_or_none()

            if not receipt_model:
                raise NotFoundException()

            receipt_model.receipt_data = receipt_data
            await self.session.commit()
            await self.session.refresh(receipt_model)

            return self._model_to_entity(receipt_model)

        except NotFoundException:
            raise
        except Exception as e:
            await self.session.rollback()
            raise InternalException() from e

    async def receipt_exists_for_purchase(self, purchase_id: UUID) -> bool:
        """Verificar si ya existe un recibo para una compra"""
        try:
            stmt = select(ReceiptModel.receipt_id).where(
                ReceiptModel.purchase_id == purchase_id)
            result = await self.session.execute(stmt)
            return result.scalar_one_or_none() is not None

        except Exception as e:
            raise InternalException() from e

    async def delete_receipt(self, receipt_id: UUID) -> bool:
        """Eliminar un recibo"""
        try:
            stmt = select(ReceiptModel).where(
                ReceiptModel.receipt_id == receipt_id)
            result = await self.session.execute(stmt)
            receipt_model = result.scalar_one_or_none()

            if not receipt_model:
                return False

            await self.session.delete(receipt_model)
            await self.session.commit()

            return True

        except Exception as e:
            await self.session.rollback()
            raise InternalException() from e

    def _model_to_entity(self, receipt_model: ReceiptModel) -> Receipt:
        """Convertir modelo SQLAlchemy a entidad de dominio"""
        return Receipt(
            receipt_id=receipt_model.receipt_id,
            purchase_id=receipt_model.purchase_id,
            receipt_data=receipt_model.receipt_data,
            generated_at=receipt_model.generated_at
        )
