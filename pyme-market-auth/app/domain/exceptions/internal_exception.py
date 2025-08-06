from app.domain.exceptions.status_exception import StatusException
from app.domain.entities.status import Status

class InternalException(StatusException):
    def __init__(self) -> None:
        super().__init__(status=Status(code="05",description="System error"), status_code=500)
