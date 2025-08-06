from decouple import config
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
import socket


class DataBaseConfig():
    def __init__(self):
        self.DB_HOST = config('DB_HOST', default='127.0.0.1')
        self.DB_PORT = config('DB_PORT', default=5432, cast=int)
        self.DB_NAME = config('DB_NAME', default='products')
        self.DB_USER = config('DB_USER')
        self.DB_PASSWORD = config('DB_PASSWORD')

        try:
            socket.gethostbyname(self.DB_HOST)
        except socket.gaierror as e:
            self.DB_HOST = '127.0.0.1'

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
