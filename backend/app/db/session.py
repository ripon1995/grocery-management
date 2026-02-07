from typing import Any, AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from app.core.config import settings

# DATABASE_URL = 'postgresql://postgres.vzmtnbuubvoaryhajwpu:groceryManager%401234@aws-1-ap-south-1.pooler.supabase.com:6543/postgres'


engine = create_async_engine(
    settings.DATABASE_URL,
    echo=True,
    future=True,
    connect_args={
        "prepared_statement_cache_size": 0,
        "statement_cache_size": 0
    }
)

async_session_factory = async_sessionmaker(
    engine,
    expire_on_commit=False,
    class_=AsyncSession
)


async def get_db() -> AsyncGenerator[AsyncSession | Any, Any]:
    async with async_session_factory() as session:
        yield session
