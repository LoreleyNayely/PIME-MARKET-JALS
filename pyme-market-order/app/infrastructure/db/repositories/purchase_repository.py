from typing import Optional, List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from app.domain.entities.purchase import Purchase
from app.infrastructure.db.models.purchase_model import PurchaseModel
from app.schemas.purchase_schema import PurchaseCreate
from app.domain.exceptions.not_found_exception import NotFoundException
from app.domain.exceptions.internal_exception import InternalException


class PurchaseRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_purchase(self, purchase_data: PurchaseCreate) -> Purchase:
        """Crear una nueva compra"""
        try:
            final_amount = purchase_data.total_amount - \
                purchase_data.discount_amount + purchase_data.tax_amount

            purchase_model = PurchaseModel(
                cart_id=purchase_data.cart_id,
                user_id=purchase_data.user_id,
                purchase_number=purchase_data.purchase_number,
                total_amount=purchase_data.total_amount,
                tax_amount=purchase_data.tax_amount,
                discount_amount=purchase_data.discount_amount,
                final_amount=final_amount,
                payment_method=purchase_data.payment_method,
                status="completed"
            )

            self.session.add(purchase_model)
            await self.session.commit()
            await self.session.refresh(purchase_model)

            return self._model_to_entity(purchase_model)

        except IntegrityError as e:
            await self.session.rollback()
            error_details = str(e.orig) if hasattr(e, 'orig') else str(e)
            raise InternalException(
                f"Database integrity error when creating purchase: {error_details}") from e
        except Exception as e:
            await self.session.rollback()
            raise InternalException(
                f"Database error when creating purchase: {type(e).__name__}: {str(e)}") from e

    async def get_purchase_by_id(self, purchase_id: UUID) -> Optional[Purchase]:
        """Obtener compra por ID"""
        try:
            stmt = select(PurchaseModel).where(
                PurchaseModel.purchase_id == purchase_id)
            result = await self.session.execute(stmt)
            purchase_model = result.scalar_one_or_none()

            if purchase_model:
                return self._model_to_entity(purchase_model)
            return None

        except Exception as e:
            raise InternalException(
                f"Error getting purchase by ID {purchase_id}: {type(e).__name__}: {str(e)}") from e

    async def get_purchase_by_cart_id(self, cart_id: UUID) -> Optional[Purchase]:
        """Obtener compra por ID del carrito"""
        try:
            stmt = select(PurchaseModel).where(
                PurchaseModel.cart_id == cart_id)
            result = await self.session.execute(stmt)
            purchase_model = result.scalar_one_or_none()

            if purchase_model:
                return self._model_to_entity(purchase_model)
            return None

        except Exception as e:
            raise InternalException(
                f"Error getting purchase by cart ID {cart_id}: {type(e).__name__}: {str(e)}") from e

    async def get_purchase_by_number(self, purchase_number: str) -> Optional[Purchase]:
        """Obtener compra por número de compra"""
        try:
            stmt = select(PurchaseModel).where(
                PurchaseModel.purchase_number == purchase_number)
            result = await self.session.execute(stmt)
            purchase_model = result.scalar_one_or_none()

            if purchase_model:
                return self._model_to_entity(purchase_model)
            return None

        except Exception as e:
            raise InternalException(
                f"Error getting purchase by number {purchase_number}: {type(e).__name__}: {str(e)}") from e

    async def get_purchases_by_user(self, user_id: str) -> List[Purchase]:
        """Obtener todas las compras de un usuario"""
        try:
            stmt = select(PurchaseModel).where(
                PurchaseModel.user_id == user_id
            ).order_by(PurchaseModel.purchased_at.desc())

            result = await self.session.execute(stmt)
            purchase_models = result.scalars().all()

            return [self._model_to_entity(model) for model in purchase_models]

        except Exception as e:
            raise InternalException(
                f"Error getting purchases for user {user_id}: {type(e).__name__}: {str(e)}") from e

    async def update_purchase_number(self, purchase_id: UUID, purchase_number: str) -> Purchase:
        """Actualizar número de compra"""
        try:
            stmt = select(PurchaseModel).where(
                PurchaseModel.purchase_id == purchase_id)
            result = await self.session.execute(stmt)
            purchase_model = result.scalar_one_or_none()

            if not purchase_model:
                raise NotFoundException()

            purchase_model.purchase_number = purchase_number
            await self.session.commit()
            await self.session.refresh(purchase_model)

            return self._model_to_entity(purchase_model)

        except NotFoundException:
            raise
        except Exception as e:
            await self.session.rollback()
            raise InternalException(
                f"Error updating purchase number for {purchase_id}: {type(e).__name__}: {str(e)}") from e

    async def update_purchase_amounts(self, purchase_id: UUID, total_amount: float,
                                      tax_amount: float, discount_amount: float, final_amount: float) -> Purchase:
        """Actualizar montos de la compra"""
        try:
            stmt = select(PurchaseModel).where(
                PurchaseModel.purchase_id == purchase_id)
            result = await self.session.execute(stmt)
            purchase_model = result.scalar_one_or_none()

            if not purchase_model:
                raise NotFoundException()

            purchase_model.total_amount = total_amount
            purchase_model.tax_amount = tax_amount
            purchase_model.discount_amount = discount_amount
            purchase_model.final_amount = final_amount

            await self.session.commit()
            await self.session.refresh(purchase_model)

            return self._model_to_entity(purchase_model)

        except NotFoundException:
            raise
        except Exception as e:
            await self.session.rollback()
            raise InternalException(
                f"Error updating purchase amounts for {purchase_id}: {type(e).__name__}: {str(e)}") from e

    async def update_payment_method(self, purchase_id: UUID, payment_method: str) -> Purchase:
        """Actualizar método de pago"""
        try:
            stmt = select(PurchaseModel).where(
                PurchaseModel.purchase_id == purchase_id)
            result = await self.session.execute(stmt)
            purchase_model = result.scalar_one_or_none()

            if not purchase_model:
                raise NotFoundException()

            purchase_model.payment_method = payment_method
            await self.session.commit()
            await self.session.refresh(purchase_model)

            return self._model_to_entity(purchase_model)

        except NotFoundException:
            raise
        except Exception as e:
            await self.session.rollback()
            raise InternalException(
                f"Error updating payment method for {purchase_id}: {type(e).__name__}: {str(e)}") from e

    async def purchase_exists_for_cart(self, cart_id: UUID) -> bool:
        """Verificar si ya existe una compra para un carrito"""
        try:
            stmt = select(PurchaseModel.purchase_id).where(
                PurchaseModel.cart_id == cart_id)
            result = await self.session.execute(stmt)
            return result.scalar_one_or_none() is not None

        except Exception as e:
            raise InternalException(
                f"Error checking if purchase exists for cart {cart_id}: {type(e).__name__}: {str(e)}") from e

    def _model_to_entity(self, purchase_model: PurchaseModel) -> Purchase:
        """Convertir modelo SQLAlchemy a entidad de dominio"""
        return Purchase(
            purchase_id=purchase_model.purchase_id,
            cart_id=purchase_model.cart_id,
            user_id=purchase_model.user_id,
            purchase_number=purchase_model.purchase_number,
            total_amount=purchase_model.total_amount,
            tax_amount=purchase_model.tax_amount,
            discount_amount=purchase_model.discount_amount,
            final_amount=purchase_model.final_amount,
            payment_method=purchase_model.payment_method,
            status=purchase_model.status,
            purchased_at=purchase_model.purchased_at
        )
