from typing import Any, Dict, Optional
import httpx

from app.domain.entities.status import Status
from app.domain.exceptions.status_exception import StatusException
from app.domain.exceptions.internal_exception import InternalException

async def request(method: str, url:str, headers: Optional[Dict[str, str]] = None, params: Optional[Dict[str, Any]] = None, json: Optional[Dict[str, Any]] = None) -> Any:
    try:
        async with httpx.AsyncClient() as client:
            response = await client.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                json=json)
            response.raise_for_status()
            return {'headers': response.headers, 'body': response.json()}
    except httpx.HTTPStatusError as exc:
        raise StatusException(
            status_code=exc.response.status_code,
            status=Status.model_validate_json(exc.response.text)) from exc
    except Exception as exc:
        raise InternalException() from exc
    finally:
        await client.aclose()
