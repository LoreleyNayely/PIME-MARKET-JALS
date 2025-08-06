from app.domain.exceptions.status_exception import StatusException
from app.domain.entities.status import Status


class PurchaseException(StatusException):
    def __init__(self, message: str, code: str = "PURCH000"):
        status = Status(code=code, description=message)
        super().__init__(status_code=400, status=status)


class PurchaseNotFoundException(StatusException):
    def __init__(self, purchase_id: str = None, purchase_number: str = None):
        if purchase_id:
            message = f"Purchase with ID {purchase_id} not found"
        elif purchase_number:
            message = f"Purchase with number {purchase_number} not found"
        else:
            message = "Purchase not found"

        status = Status(code="PURCH001", description=message)
        super().__init__(status_code=404, status=status)


class PurchaseAlreadyExistsException(StatusException):
    def __init__(self, cart_id: str):
        message = f"Purchase for cart {cart_id} already exists"
        status = Status(code="PURCH002", description=message)
        super().__init__(status_code=409, status=status)


class InvalidAmountException(StatusException):
    def __init__(self, amount_type: str, amount: float = None):
        if amount is not None:
            if amount < 0:
                message = f"{amount_type} cannot be negative, got {amount}"
            else:
                message = f"Invalid {amount_type}: {amount}"
        else:
            message = f"Invalid {amount_type} provided"

        status = Status(code="PURCH003", description=message)
        super().__init__(status_code=400, status=status)


class InvalidDiscountException(StatusException):
    def __init__(self, discount: float, total_amount: float = None):
        if total_amount and discount > total_amount:
            message = f"Discount amount {discount} cannot exceed total amount {total_amount}"
        elif discount < 0:
            message = f"Discount cannot be negative, got {discount}"
        elif discount > 100:
            message = f"Discount percentage cannot exceed 100%, got {discount}%"
        else:
            message = f"Invalid discount: {discount}"

        status = Status(code="PURCH004", description=message)
        super().__init__(status_code=400, status=status)


class InvalidPaymentMethodException(StatusException):
    def __init__(self, payment_method: str):
        allowed_methods = ['cash', 'card', 'transfer']
        message = f"Payment method '{payment_method}' is invalid. Allowed methods: {', '.join(allowed_methods)}"
        status = Status(code="PURCH005", description=message)
        super().__init__(status_code=400, status=status)


class PurchaseProcessingException(StatusException):
    def __init__(self, cart_id: str, reason: str = None):
        if reason:
            message = f"Cannot process purchase for cart {cart_id}: {reason}"
        else:
            message = f"Cannot process purchase for cart {cart_id}"

        status = Status(code="PURCH006", description=message)
        super().__init__(status_code=400, status=status)


class InsufficientStockException(StatusException):
    def __init__(self, product_sku: str, available_stock: int, requested_quantity: int):
        message = f"Insufficient stock for product {product_sku}. Available: {available_stock}, Requested: {requested_quantity}"
        status = Status(code="PURCH007", description=message)
        super().__init__(status_code=400, status=status)
