import asyncpg
from sqlalchemy import MetaData

metadata = MetaData()


async def create_connection_pool(_app, *args, **kwargs):
    config = _app["SETTINGS"].POSTGRES.configuration_dict
    pool = await asyncpg.create_pool(min_size=1, max_size=5, **config)
    _app["pool"] = pool


async def close_connection_pool(_app, *args, **kwargs):
    await _app["pool"].close()
