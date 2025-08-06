from app.domain.entities.status import Status


class StatusException(Exception):
    def __init__(self, status: Status, status_code: int) -> None:
        self.status = status
        self.status_code = status_code
