from app.domain.exceptions.status_exception import StatusException
from app.domain.entities.status import Status


class CartException(StatusException):
    def __init__(self, message: str, code: str = "CART000"):
        status = Status(code=code, description=message)
        super().__init__(status_code=400, status=status)


class CartNotFoundException(StatusException):
    def __init__(self, cart_id: str = None, user_id: str = None):
        if cart_id:
            message = f"Cart with ID {cart_id} not found"
        elif user_id:
            message = f"Active cart for user {user_id} not found"
        else:
            message = "Cart not found"

        status = Status(code="CART001", description=message)
        super().__init__(status_code=404, status=status)


class CartAlreadyCompletedException(StatusException):
    def __init__(self, cart_id: str):
        message = f"Cart {cart_id} is already completed and cannot be modified"
        status = Status(code="CART002", description=message)
        super().__init__(status_code=400, status=status)


class CartIsEmptyException(StatusException):
    def __init__(self, cart_id: str = None):
        message = f"Cart {cart_id or ''} is empty and cannot be processed".strip()
        status = Status(code="CART003", description=message)
        super().__init__(status_code=400, status=status)


class CartInactiveException(StatusException):
    def __init__(self, cart_id: str):
        message = f"Cart {cart_id} is inactive and cannot be used"
        status = Status(code="CART004", description=message)
        super().__init__(status_code=400, status=status)


class CartAbandonedException(StatusException):
    def __init__(self, cart_id: str):
        message = f"Cart {cart_id} has been abandoned and cannot be processed"
        status = Status(code="CART005", description=message)
        super().__init__(status_code=400, status=status)


class InvalidCartStatusException(StatusException):
    def __init__(self, current_status: str, required_status: str = None):
        if required_status:
            message = f"Cart status is '{current_status}', but '{required_status}' is required"
        else:
            message = f"Invalid cart status: '{current_status}'"

        status = Status(code="CART006", description=message)
        super().__init__(status_code=400, status=status)
