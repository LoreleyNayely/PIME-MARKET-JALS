from decouple import config
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession


class DataBaseConfig():
    DB_HOST = config('DB_HOST')
    DB_PORT = config('DB_PORT')
    DB_NAME = config('DB_NAME')
    DB_USER = config('DB_USER')
    DB_PASSWORD = config('DB_PASSWORD')

    @property
    def async_database_url_constructed(self):
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


database_settings = DataBaseConfig()

engine = create_async_engine(
    database_settings.async_database_url_constructed,
    echo=True
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autoflush=False,
    autocommit=False
)
