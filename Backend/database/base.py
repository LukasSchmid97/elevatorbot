import asyncio
import os
from contextlib import asynccontextmanager, suppress
from typing import AsyncContextManager, Optional

import orjson
from sqlalchemy.engine import Engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from Shared.functions.readSettingsFile import get_setting

POSTGRES_USER = os.environ.get("POSTGRES_USER")
assert POSTGRES_USER
POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD")
assert POSTGRES_PASSWORD
POSTGRES_HOST = os.environ.get("POSTGRES_HOST")
assert POSTGRES_HOST
POSTGRES_PORT = os.environ.get("POSTGRES_PORT")
assert POSTGRES_PORT
POSTGRES_DB = os.environ.get("POSTGRES_DB")
assert POSTGRES_DB

# max DB connections
MAX_DB_CONNECTIONS = 80
# how long to wait for a free db connection
WAIT_FOR_DB_CONNECTION = 180

DATABASE_URL = (
    f"""postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"""
)
_ENGINE = None
_SESSIONMAKER = None
_TEST_MODE = False


Base = declarative_base()


def setup_engine(database_url: str = DATABASE_URL) -> Engine:
    global _ENGINE

    if not _ENGINE:
        _ENGINE = create_async_engine(
            database_url,
            future=True,
            echo=bool(get_setting("ENABLE_DEBUG_MODE") and not is_test_mode()),
            echo_pool=bool(get_setting("ENABLE_DEBUG_MODE") and not is_test_mode()),
            json_deserializer=orjson.loads,
            json_serializer=lambda x: orjson.dumps(x).decode(),
            pool_pre_ping=True,
            pool_size=50,
            max_overflow=50,
            pool_timeout=300,
        )

    return _ENGINE


def get_async_sessionmaker() -> sessionmaker:
    global _SESSIONMAKER

    # if expire_on_commit is enabled, our own cache would get expired after every session close
    # since we are careful and update the cache when we change an object, that should not be a problem
    if not _SESSIONMAKER:
        _SESSIONMAKER = sessionmaker(bind=setup_engine(), class_=AsyncSession, future=True, expire_on_commit=False)
    return _SESSIONMAKER


def is_test_mode(set_test_mode: Optional[bool] = None) -> bool:
    global _TEST_MODE

    if set_test_mode is not None:
        _TEST_MODE = set_test_mode

    return _TEST_MODE


db_semaphore = asyncio.Semaphore(MAX_DB_CONNECTIONS)


@asynccontextmanager
async def acquire_db_session() -> AsyncContextManager[AsyncSession]:
    """Get a database session"""

    async def _wait_for_semaphore():
        await db_semaphore.acquire()

    await asyncio.wait_for(asyncio.shield(_wait_for_semaphore()), timeout=WAIT_FOR_DB_CONNECTION)

    try:
        async with get_async_sessionmaker().begin() as session:
            yield session
    finally:
        db_semaphore.release()
