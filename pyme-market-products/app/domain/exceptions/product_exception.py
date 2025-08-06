from app.domain.exceptions.status_exception import StatusException
from app.domain.entities.status import Status


class ProductException(StatusException):
    def __init__(self, message: str, code: str = "PROD000"):
        status = Status(code=code, description=message)
        super().__init__(status_code=400, status=status)


class ProductNotFoundException(StatusException):
    def __init__(self, product_id: str = None, sku: str = None):
        if product_id:
            message = f"Product with ID {product_id} not found"
        elif sku:
            message = f"Product with SKU {sku} not found"
        else:
            message = "Product not found"

        status = Status(code="PROD001", description=message)
        super().__init__(status_code=404, status=status)


class DuplicateSkuException(StatusException):
    def __init__(self, sku: str):
        message = f"Product with SKU '{sku}' already exists"
        status = Status(code="PROD002", description=message)
        super().__init__(status_code=409, status=status)


class InvalidStockException(StatusException):
    def __init__(self, message: str = "Invalid stock quantity"):
        status = Status(code="PROD003", description=message)
        super().__init__(status_code=400, status=status)


class InvalidPriceException(StatusException):
    def __init__(self, message: str = "Invalid price value"):
        status = Status(code="PROD004", description=message)
        super().__init__(status_code=400, status=status)


class ProductInactiveException(StatusException):
    def __init__(self, sku: str = None):
        message = f"Product {sku if sku else ''} is inactive and cannot be used"
        status = Status(code="PROD005", description=message.strip())
        super().__init__(status_code=400, status=status)
