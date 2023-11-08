from aiohttp import web

# from aiohttp_apispec import setup_aiohttp_apispec as _setup_aiohttp_apispec
from aiohttp_apispec import validation_middleware
from aiohttp_middlewares import cors_middleware

from ll.logger import setup_logging
from ll.sentry import setup_sentry

from ..storage.db import close_connection_pool, create_connection_pool
from .handlers import setup_api_routes
from .healthcheck import setup_healthcheck_routes
from .middlewares import http_error_middleware
from .settings import Settings


def setup_settings(_app):
    """Load config on app startup."""
    _app["SETTINGS"] = Settings()


def app_factory():
    _app = web.Application(middlewares=[cors_middleware(allow_all=True)])
    setup_settings(_app)
    setup_sentry(_app["SETTINGS"].SENTRY, _app["SETTINGS"].BUILD_VERSION)
    setup_logging(_app["SETTINGS"].LOG_LEVEL)

    # Schemas
    # _setup_aiohttp_apispec(app=_app, **_get_swagger_config(_app))
    _app.middlewares.extend([http_error_middleware, validation_middleware])

    # Handlers
    setup_api_routes(_app)
    setup_healthcheck_routes(_app)
    # Start up
    _app.on_startup.extend([create_connection_pool])

    # Clean up
    _app.on_cleanup.extend([close_connection_pool])

    return _app


def _get_swagger_config(_app):
    """
    Configure Swagger UI.

    We only publish our Swagger dogs for development builds.
    """
    return (
        {
            "url": "/legless-lizard/docs/swagger.json",
            "swagger_path": "/legless-lizard/docs/",
            "static_path": "/legless-lizard/swagger",
        }
        if _app["SETTINGS"].API_DOCS
        else {}
    )


async def create_app():
    return app_factory()
