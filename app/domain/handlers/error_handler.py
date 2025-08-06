from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

from app.domain.exceptions.status_exception import StatusException


async def status_exception_handler(request: Request, exc: StatusException):
    return JSONResponse(
        status_code=exc.status_code,
        content=jsonable_encoder(exc.status)
    )


async def exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={'code': '05', 'description': 'System Error'}
    )
