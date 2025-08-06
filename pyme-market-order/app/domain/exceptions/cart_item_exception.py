from app.domain.exceptions.status_exception import StatusException
from app.domain.entities.status import Status


class CartItemException(StatusException):
    def __init__(self, message: str, code: str = "ITEM000"):
        status = Status(code=code, description=message)
        super().__init__(status_code=400, status=status)


class CartItemNotFoundException(StatusException):
    def __init__(self, cart_item_id: str = None, product_id: str = None):
        if cart_item_id:
            message = f"Cart item with ID {cart_item_id} not found"
        elif product_id:
            message = f"Product {product_id} not found in cart"
        else:
            message = "Cart item not found"

        status = Status(code="ITEM001", description=message)
        super().__init__(status_code=404, status=status)


class InvalidQuantityException(StatusException):
    def __init__(self, quantity: int = None, max_quantity: int = 999):
        if quantity is not None:
            if quantity <= 0:
                message = f"Quantity must be greater than 0, got {quantity}"
            elif quantity > max_quantity:
                message = f"Quantity cannot exceed {max_quantity}, got {quantity}"
            else:
                message = f"Invalid quantity: {quantity}"
        else:
            message = "Invalid quantity provided"

        status = Status(code="ITEM002", description=message)
        super().__init__(status_code=400, status=status)


class ProductAlreadyInCartException(StatusException):
    def __init__(self, product_id: str, product_sku: str = None):
        if product_sku:
            message = f"Product {product_sku} (ID: {product_id}) is already in the cart"
        else:
            message = f"Product {product_id} is already in the cart"

        status = Status(code="ITEM003", description=message)
        super().__init__(status_code=409, status=status)


class InvalidPriceException(StatusException):
    def __init__(self, price: float = None):
        if price is not None:
            if price <= 0:
                message = f"Price must be greater than 0, got {price}"
            else:
                message = f"Invalid price: {price}"
        else:
            message = "Invalid price provided"

        status = Status(code="ITEM004", description=message)
        super().__init__(status_code=400, status=status)


class ProductDataIncompleteException(StatusException):
    def __init__(self, missing_fields: list):
        message = f"Product data incomplete. Missing fields: {', '.join(missing_fields)}"
        status = Status(code="ITEM005", description=message)
        super().__init__(status_code=400, status=status)
