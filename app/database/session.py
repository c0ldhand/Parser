from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from typing import AsyncGenerator
from app.config import config

engine = create_async_engine(
    url = config.DATABASE_URL_AIOSQLITE,
    echo=False,
)

async_session_factory = async_sessionmaker(
    engine,
    expire_on_commit=False,
)

async def get_async_session() -> AsyncGenerator:
    """Метод для получения асинхронной сессии"""
    async with async_session_factory() as session:
        yield session
