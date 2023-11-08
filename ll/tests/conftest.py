import asyncio
from unittest import mock

import asyncpg
import pytest
import structlog
from aiohttp.test_utils import TestClient, TestServer

from ll.api.app import app_factory
from ll.storage.settings import PostgresSettings

from .db import (
    TestPostgresSettings,
    delete_db,
    ensure_db,
    mock_create_connection_pool_factory,
)

logger = structlog.get_logger(__name__)
config = PostgresSettings().configuration_dict


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def db():
    """Create a test database."""
    await ensure_db()
    settings = TestPostgresSettings()
    conn = await asyncpg.connect(**settings.configuration_dict)

    yield conn

    await conn.close()

    await delete_db()


@pytest.fixture(scope="function")
async def conn(db):
    """Return a database connection that is rolled back after a test completes."""
    tr = db.transaction()
    await tr.start()
    yield db
    await tr.rollback()


@pytest.fixture(scope="function")
async def client(db):
    mock_create_connection_pool = mock_create_connection_pool_factory(db)
    with mock.patch("ll.api.app.create_connection_pool", mock_create_connection_pool):
        app = app_factory()

    server = TestServer(app)
    client = TestClient(server)

    await client.start_server()

    yield client

    await client.close()
