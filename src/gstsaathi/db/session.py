from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from gstsaathi.config import Settings
from gstsaathi.db.url import to_asyncpg_url


def make_engine(settings: Settings):
    database_url = to_asyncpg_url(settings.database_url)

    return create_async_engine(
        database_url,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=10,
    )


def make_sessionmaker(engine):
    return async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
