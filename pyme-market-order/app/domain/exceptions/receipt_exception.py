from app.domain.exceptions.status_exception import StatusException
from app.domain.entities.status import Status


class ReceiptException(StatusException):
    def __init__(self, message: str, code: str = "RCPT000"):
        status = Status(code=code, description=message)
        super().__init__(status_code=400, status=status)


class ReceiptNotFoundException(StatusException):
    def __init__(self, receipt_id: str = None, purchase_id: str = None):
        if receipt_id:
            message = f"Receipt with ID {receipt_id} not found"
        elif purchase_id:
            message = f"Receipt for purchase {purchase_id} not found"
        else:
            message = "Receipt not found"

        status = Status(code="RCPT001", description=message)
        super().__init__(status_code=404, status=status)


class ReceiptAlreadyExistsException(StatusException):
    def __init__(self, purchase_id: str):
        message = f"Receipt for purchase {purchase_id} already exists"
        status = Status(code="RCPT002", description=message)
        super().__init__(status_code=409, status=status)


class ReceiptGenerationException(StatusException):
    def __init__(self, purchase_id: str, reason: str = None):
        if reason:
            message = f"Cannot generate receipt for purchase {purchase_id}: {reason}"
        else:
            message = f"Cannot generate receipt for purchase {purchase_id}"

        status = Status(code="RCPT003", description=message)
        super().__init__(status_code=500, status=status)


class InvalidReceiptDataException(StatusException):
    def __init__(self, missing_fields: list = None, invalid_fields: list = None):
        if missing_fields and invalid_fields:
            message = f"Receipt data error. Missing fields: {', '.join(missing_fields)}. Invalid fields: {', '.join(invalid_fields)}"
        elif missing_fields:
            message = f"Receipt data incomplete. Missing fields: {', '.join(missing_fields)}"
        elif invalid_fields:
            message = f"Receipt data invalid. Invalid fields: {', '.join(invalid_fields)}"
        else:
            message = "Invalid receipt data"

        status = Status(code="RCPT004", description=message)
        super().__init__(status_code=400, status=status)
