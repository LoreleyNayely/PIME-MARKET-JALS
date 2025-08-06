from typing import List, Optional
from uuid import UUID
from decimal import Decimal
from app.domain.entities.product import Product
from app.schemas.product_schema import ProductCreate, ProductUpdate
from app.infrastructure.db.repositories.product_repository import ProductRepository
from app.domain.exceptions.product_exception import (
    ProductNotFoundException,
    DuplicateSkuException,
    InvalidStockException,
    InvalidPriceException,
    ProductInactiveException
)


class ProductService:
    def __init__(self, product_repository: ProductRepository):
        self.product_repository = product_repository

    async def create_product(self, product_data: ProductCreate) -> Product:
        """Crear un nuevo producto con validaciones de negocio"""
        try:
            if await self.product_repository.sku_exists(product_data.sku):
                raise DuplicateSkuException(product_data.sku)

            self._validate_price(product_data.price)
            self._validate_stock(product_data.stock_quantity)
            self._validate_product_name(product_data.name)

            return await self.product_repository.create_product(product_data)

        except DuplicateSkuException:
            raise
        except Exception as e:
            raise Exception(f"Error creating product: {str(e)}") from e

    async def get_product_by_id(self, product_id: UUID) -> Product:
        """Obtener producto por ID"""
        product = await self.product_repository.get_product_by_id(product_id)
        if not product:
            raise ProductNotFoundException(product_id=str(product_id))
        return product

    async def get_product_by_sku(self, sku: str) -> Product:
        """Obtener producto por SKU"""
        product = await self.product_repository.get_product_by_sku(sku)
        if not product:
            raise ProductNotFoundException(sku=sku)
        return product

    async def get_all_products(self, include_inactive: bool = False) -> List[Product]:
        """Obtener todos los productos"""
        return await self.product_repository.get_all_products(include_inactive)

    async def update_product(self, product_id: UUID, update_data: ProductUpdate) -> Product:
        """Actualizar un producto con validaciones"""
        existing_product = await self.product_repository.get_product_by_id(product_id)
        if not existing_product:
            raise ProductNotFoundException(product_id=str(product_id))

        if update_data.sku and update_data.sku != existing_product.sku:
            if await self.product_repository.sku_exists(update_data.sku, exclude_product_id=product_id):
                raise DuplicateSkuException(update_data.sku)

        if update_data.price is not None:
            self._validate_price(update_data.price)

        if update_data.stock_quantity is not None:
            self._validate_stock(update_data.stock_quantity)

        if update_data.name is not None:
            self._validate_product_name(update_data.name)

        return await self.product_repository.update_product(product_id, update_data)

    async def delete_product(self, product_id: UUID) -> bool:
        """Eliminar (soft delete) un producto"""
        existing_product = await self.product_repository.get_product_by_id(product_id)
        if not existing_product:
            raise ProductNotFoundException(product_id=str(product_id))

        return await self.product_repository.delete_product(product_id)

    async def restore_product(self, product_id: UUID) -> bool:
        """Restaurar un producto eliminado"""
        success = await self.product_repository.restore_product(product_id)
        if not success:
            raise ProductNotFoundException(product_id=str(product_id))
        return success

    async def update_stock(self, product_id: UUID, new_stock: int) -> Product:
        """Actualizar solo el inventario de un producto"""
        existing_product = await self.product_repository.get_product_by_id(product_id)
        if not existing_product:
            raise ProductNotFoundException(product_id=str(product_id))

        if not existing_product.is_active:
            raise ProductInactiveException(existing_product.sku)

        self._validate_stock(new_stock)

        return await self.product_repository.update_stock(product_id, new_stock)

    async def check_stock_availability(self, product_id: UUID, required_quantity: int) -> bool:
        """Verificar si hay suficiente stock disponible"""
        product = await self.get_product_by_id(product_id)

        if not product.is_active:
            raise ProductInactiveException(product.sku)

        return product.stock_quantity >= required_quantity

    async def reduce_stock(self, product_id: UUID, quantity: int) -> Product:
        """Reducir stock de un producto (para ventas)"""
        product = await self.get_product_by_id(product_id)

        if not product.is_active:
            raise ProductInactiveException(product.sku)

        if product.stock_quantity < quantity:
            raise InvalidStockException(
                f"Insufficient stock. Available: {product.stock_quantity}, Required: {quantity}")

        new_stock = product.stock_quantity - quantity
        return await self.update_stock(product_id, new_stock)

    async def increase_stock(self, product_id: UUID, quantity: int) -> Product:
        """Aumentar stock de un producto (para reposiciones)"""
        product = await self.get_product_by_id(product_id)

        if not product.is_active:
            raise ProductInactiveException(product.sku)

        self._validate_stock(quantity)
        new_stock = product.stock_quantity + quantity
        return await self.update_stock(product_id, new_stock)

    def _validate_price(self, price: Decimal) -> None:
        """Validar precio"""
        if price <= 0:
            raise InvalidPriceException("Price must be greater than 0")

        if price > Decimal('999999.99'):
            raise InvalidPriceException("Price cannot exceed 999,999.99")

    def _validate_stock(self, stock: int) -> None:
        """Validar stock"""
        if stock < 0:
            raise InvalidStockException("Stock cannot be negative")

        if stock > 999999:
            raise InvalidStockException("Stock cannot exceed 999,999 units")

    def _validate_product_name(self, name: str) -> None:
        """Validar nombre del producto"""
        if not name or not name.strip():
            raise Exception("Product name cannot be empty")

        if len(name.strip()) < 2:
            raise Exception("Product name must be at least 2 characters long")


def get_product_service(product_repository: ProductRepository) -> ProductService:
    """Factory function para obtener instancia del servicio"""
    return ProductService(product_repository)
