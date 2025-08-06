from app.domain.exceptions.status_exception import StatusException
from app.domain.entities.status import Status


class InternalException(StatusException):
    def __init__(self, message: str = "System error") -> None:
        super().__init__(status=Status(code="05", description=message), status_code=500)
