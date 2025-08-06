from typing import Optional, List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.exc import IntegrityError
from app.domain.entities.product import Product
from app.infrastructure.db.models.product_model import ProductModel
from app.schemas.product_schema import ProductCreate, ProductUpdate
from app.domain.exceptions.not_found_exception import NotFoundException
from app.domain.exceptions.internal_exception import InternalException


class ProductRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_product(self, product_data: ProductCreate) -> Product:
        """Crear un nuevo producto"""
        try:
            product_model = ProductModel(
                name=product_data.name,
                description=product_data.description,
                price=product_data.price,
                stock_quantity=product_data.stock_quantity,
                sku=product_data.sku.upper().strip(),
                is_active=True
            )

            self.session.add(product_model)
            await self.session.commit()
            await self.session.refresh(product_model)

            return self._model_to_entity(product_model)

        except IntegrityError as e:
            await self.session.rollback()
            if "unique constraint" in str(e).lower() and "sku" in str(e).lower():
                raise InternalException() from e
            raise InternalException() from e
        except Exception as e:
            await self.session.rollback()
            raise InternalException() from e

    async def get_product_by_id(self, product_id: UUID) -> Optional[Product]:
        """Obtener producto por ID"""
        try:
            stmt = select(ProductModel).where(
                ProductModel.product_id == product_id)
            result = await self.session.execute(stmt)
            product_model = result.scalar_one_or_none()

            if product_model:
                return self._model_to_entity(product_model)
            return None

        except Exception as e:
            raise InternalException() from e

    async def get_product_by_sku(self, sku: str) -> Optional[Product]:
        """Obtener producto por SKU"""
        try:
            stmt = select(ProductModel).where(
                ProductModel.sku == sku.upper().strip())
            result = await self.session.execute(stmt)
            product_model = result.scalar_one_or_none()

            if product_model:
                return self._model_to_entity(product_model)
            return None

        except Exception as e:
            raise InternalException() from e

    async def get_all_products(self, include_inactive: bool = False) -> List[Product]:
        """Obtener todos los productos"""
        try:
            if include_inactive:
                stmt = select(ProductModel).order_by(
                    ProductModel.created_at.desc())
            else:
                stmt = select(ProductModel).where(
                    ProductModel.is_active == True
                ).order_by(ProductModel.created_at.desc())

            result = await self.session.execute(stmt)
            product_models = result.scalars().all()

            return [self._model_to_entity(model) for model in product_models]

        except Exception as e:
            raise InternalException() from e

    async def update_product(self, product_id: UUID, update_data: ProductUpdate) -> Product:
        """Actualizar un producto"""
        try:
            stmt = select(ProductModel).where(
                ProductModel.product_id == product_id)
            result = await self.session.execute(stmt)
            product_model = result.scalar_one_or_none()

            if not product_model:
                raise NotFoundException()

            update_dict = update_data.model_dump(exclude_unset=True)

            for field, value in update_dict.items():
                if hasattr(product_model, field) and value is not None:
                    if field == 'sku' and value:
                        value = value.upper().strip()
                    setattr(product_model, field, value)

            await self.session.commit()
            await self.session.refresh(product_model)

            return self._model_to_entity(product_model)

        except NotFoundException:
            raise
        except IntegrityError as e:
            await self.session.rollback()
            if "unique constraint" in str(e).lower() and "sku" in str(e).lower():
                raise InternalException() from e
            raise InternalException() from e
        except Exception as e:
            await self.session.rollback()
            raise InternalException() from e

    async def delete_product(self, product_id: UUID) -> bool:
        """Soft delete de un producto"""
        try:
            stmt = select(ProductModel).where(
                ProductModel.product_id == product_id)
            result = await self.session.execute(stmt)
            product_model = result.scalar_one_or_none()

            if not product_model:
                return False

            product_model.is_active = False
            await self.session.commit()

            return True

        except Exception as e:
            await self.session.rollback()
            raise InternalException() from e

    async def restore_product(self, product_id: UUID) -> bool:
        """Restaurar un producto eliminado (soft delete)"""
        try:
            stmt = select(ProductModel).where(
                and_(
                    ProductModel.product_id == product_id,
                    ProductModel.is_active == False
                )
            )
            result = await self.session.execute(stmt)
            product_model = result.scalar_one_or_none()

            if not product_model:
                return False

            product_model.is_active = True
            await self.session.commit()

            return True

        except Exception as e:
            await self.session.rollback()
            raise InternalException() from e

    async def sku_exists(self, sku: str, exclude_product_id: Optional[UUID] = None) -> bool:
        """Verificar si un SKU ya existe"""
        try:
            sku_clean = sku.upper().strip()

            if exclude_product_id:
                stmt = select(ProductModel.product_id).where(
                    and_(
                        ProductModel.sku == sku_clean,
                        ProductModel.product_id != exclude_product_id
                    )
                )
            else:
                stmt = select(ProductModel.product_id).where(
                    ProductModel.sku == sku_clean)

            result = await self.session.execute(stmt)
            return result.scalar_one_or_none() is not None

        except Exception as e:
            raise InternalException() from e

    async def update_stock(self, product_id: UUID, new_stock: int) -> Product:
        """Actualizar solo el stock de un producto"""
        try:
            stmt = select(ProductModel).where(
                ProductModel.product_id == product_id)
            result = await self.session.execute(stmt)
            product_model = result.scalar_one_or_none()

            if not product_model:
                raise NotFoundException()

            product_model.stock_quantity = new_stock
            await self.session.commit()
            await self.session.refresh(product_model)

            return self._model_to_entity(product_model)

        except NotFoundException:
            raise
        except Exception as e:
            await self.session.rollback()
            raise InternalException() from e

    def _model_to_entity(self, product_model: ProductModel) -> Product:
        """Convertir modelo SQLAlchemy a entidad de dominio"""
        return Product(
            product_id=product_model.product_id,
            name=product_model.name,
            description=product_model.description,
            price=product_model.price,
            stock_quantity=product_model.stock_quantity,
            sku=product_model.sku,
            is_active=product_model.is_active,
            created_at=product_model.created_at,
            updated_at=product_model.updated_at
        )
