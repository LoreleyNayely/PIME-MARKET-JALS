from app.domain.exceptions.status_exception import StatusException
from app.domain.entities.status import Status


class AuthException(StatusException):
    def __init__(self, message: str, code: str = "AUTH000"):
        status = Status(code=code, description=message)
        super().__init__(status_code=401, status=status)


class InvalidCredentialsException(AuthException):
    def __init__(self):
        super().__init__(message="Invalid credentials", code="AUTH001")


class TokenExpiredException(AuthException):
    def __init__(self):
        super().__init__(message="Token has expired", code="AUTH002")


class InvalidTokenException(AuthException):
    def __init__(self):
        super().__init__(message="Invalid token", code="AUTH003")


class UserNotActiveException(AuthException):
    def __init__(self):
        super().__init__(message="User account is not active", code="AUTH004")


class WeakPasswordException(StatusException):
    def __init__(self, message: str = "Password does not meet security requirements"):
        status = Status(code="AUTH005", description=message)
        super().__init__(status_code=400, status=status)
