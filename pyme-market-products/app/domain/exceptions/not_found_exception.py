from app.domain.exceptions.status_exception import StatusException
from app.domain.entities.status import Status

class NotFoundException(StatusException):
    def __init__(self) -> None:
        super().__init__(status=Status(code="12", description="Invalid transaction"), status_code=404)
