from contextlib import asynccontextmanager

import asyncpg
import structlog
from alembic.command import upgrade
from alembic.config import Config
from pydantic import Field, validator
from sqlalchemy.ext.asyncio import create_async_engine

from ll.storage.settings import PostgresSettings

logger = structlog.get_logger(__name__)


class TestPostgresSettings(PostgresSettings):
    DATABASE: str = Field(alias="POSTGRES_DB")

    @validator("DATABASE", always=True)
    def test_database(cls, v, values, **kwargs):
        return "test_" + v


class MockPool:
    def __init__(self, conn):
        self.conn = conn

    @asynccontextmanager
    async def acquire(self):
        yield self.conn

    async def release(self, conn):
        pass

    async def close(self):
        pass


def mock_create_connection_pool_factory(conn):
    mock_pool = MockPool(conn=conn)

    async def mock_create_connection_pool(_app, *args, **kwargs):
        _app["pool"] = mock_pool

    return mock_create_connection_pool


@asynccontextmanager
async def _get_sys_conn():
    """Create a system connection for the purpose of preparing the app database."""
    settings = TestPostgresSettings()
    conn = await asyncpg.connect(
        database="template1",
        user=settings.USER,
        password=settings.PASSWORD,
        host=settings.HOST,
        port=settings.PORT,
    )
    try:
        yield conn
    finally:
        await conn.close()


async def ensure_db():
    settings = TestPostgresSettings()
    try:
        # Successful connection means the db exists and needs to be deleted to ensure
        # a fresh DB is set up for tests, conn
        test_conn = await asyncpg.connect(**settings.configuration_dict)
        await test_conn.close()
        await delete_db()
    except asyncpg.InvalidCatalogNameError:
        pass

    await create_db()


async def delete_db():
    settings = TestPostgresSettings()

    async with _get_sys_conn() as conn:
        stmt = f"DROP DATABASE {settings.DATABASE}"
        await conn.execute(stmt)


async def create_db():
    settings = TestPostgresSettings()
    async with _get_sys_conn() as conn:
        stmt = f"CREATE DATABASE {settings.DATABASE} OWNER {settings.USER}"
        await conn.execute(stmt)

    await run_async_upgrade(settings)


async def run_async_upgrade(settings):
    """Run alembic migration."""
    async_engine = create_async_engine(settings.connection_string)

    async with async_engine.connect() as conn:
        await conn.run_sync(run_upgrade, Config())

    await async_engine.dispose()


def run_upgrade(connection, config):
    config.attributes["connection"] = connection
    config.set_main_option("script_location", "ll/migrations")
    upgrade(config, "head")
