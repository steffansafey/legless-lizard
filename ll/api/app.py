import asyncio

from aiohttp import web
from aiohttp_apispec import setup_aiohttp_apispec, validation_middleware
from aiohttp_middlewares import cors_middleware

from ll.logger import setup_logging
from ll.sentry import setup_sentry

from ..storage.db import close_connection_pool, create_connection_pool
from .game.loop import game_loop
from .game.setup import setup_game_states
from .handlers.game import setup_api_routes
from .healthcheck import setup_healthcheck_routes
from .middlewares import http_error_middleware
from .settings import Settings
from .ws import cleanup_ws_app, setup_ws_app


def setup_settings(_app):
    """Load config on app startup."""
    _app["SETTINGS"] = Settings()


def app_factory():
    _app = web.Application(middlewares=[cors_middleware(allow_all=True)])
    setup_settings(_app)
    setup_sentry(_app["SETTINGS"].SENTRY, _app["SETTINGS"].BUILD_VERSION)
    setup_logging(_app["SETTINGS"].LOG_LEVEL)

    # Schemas
    setup_aiohttp_apispec(app=_app, **_get_swagger_config(_app))
    _app.middlewares.extend([http_error_middleware, validation_middleware])

    # Handlers
    setup_api_routes(_app)
    setup_healthcheck_routes(_app)
    setup_game_states(_app)

    # Start up
    _app.on_startup.extend(
        [create_connection_pool, setup_ws_app, create_event_loop_and_game_task]
    )

    # Clean up
    _app.on_cleanup.extend([close_connection_pool, cleanup_ws_app, close_event_loop])

    return _app


async def create_event_loop_and_game_task(_app):
    _app["loop"] = asyncio.get_event_loop()
    _app["loop"].create_task(game_loop(_app))


async def close_event_loop(_app):
    # Cancel all tasks except the current one
    tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
    for task in tasks:
        task.cancel()

    # Wait for all tasks to finish after they are cancelled
    await asyncio.gather(*tasks, return_exceptions=True)

    # Now we attempt to stop the loop
    loop = _app.get("loop", None) or asyncio.get_running_loop()
    loop.stop()


def _get_swagger_config(_app):
    """
    Configure Swagger UI.

    We only publish our Swagger dogs for development builds.
    """
    return {
        "url": "/legless-lizard/docs/swagger.json",
        "swagger_path": "/legless-lizard/docs/",
        "static_path": "/legless-lizard/swagger",
    }


async def create_app():
    return app_factory()
