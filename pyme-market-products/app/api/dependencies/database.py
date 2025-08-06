from sqlalchemy.ext.asyncio import AsyncSession
from typing import AsyncGenerator
from app.core.database_config import AsyncSessionLocal


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
