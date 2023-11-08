import asyncio
import os
import sys

import asyncpg

# Add package to sys path to allow for imports from legless-lizard
sys.path.insert(0, os.getcwd())


async def can_connect_to_postgres():
    from ll.storage.settings import PostgresSettings  # noqa

    config = PostgresSettings().configuration_dict

    try:
        conn = await asyncpg.connect(**config)
        await conn.close()
        return True
    except (asyncpg.exceptions.CannotConnectNowError, ConnectionRefusedError):
        return False


async def wait_for_postgres():
    while 1:
        if await can_connect_to_postgres():
            print("Waiting for Postgres - Ready")
            break
        else:
            print("Waiting for Postgres - Sleeping")
            await asyncio.sleep(1)


loop = asyncio.get_event_loop()
loop.run_until_complete(wait_for_postgres())
