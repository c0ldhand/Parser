from app.database.models.currency import CurrencyRate
from app.database.models.base import Base
from app.database.session import engine

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)