from typing import Optional

import sentry_sdk
from pydantic import Field
from pydantic_settings import BaseSettings
from sentry_sdk.integrations.aiohttp import AioHttpIntegration
from sentry_sdk.integrations.argv import ArgvIntegration
from sentry_sdk.integrations.atexit import AtexitIntegration
from sentry_sdk.integrations.dedupe import DedupeIntegration
from sentry_sdk.integrations.excepthook import ExcepthookIntegration
from sentry_sdk.integrations.modules import ModulesIntegration
from sentry_sdk.integrations.stdlib import StdlibIntegration
from sentry_sdk.integrations.threading import ThreadingIntegration


class SentrySettings(BaseSettings):
    SENTRY_ENVIRONMENT: str = Field(default="dev", alias="DEPLOYMENT_ENV")
    SENTRY_DSN: Optional[str] = Field(default=None, alias="SENTRY_DSN")


def setup_sentry(settings: SentrySettings, build_version: str):
    """Initialize Sentry."""

    # Do nothing if a DSN isn't specified (this is the case for local builds).
    if not settings.SENTRY_DSN:
        return

    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        release=build_version,
        environment=settings.SENTRY_ENVIRONMENT,
        # capture 1% of events - this is just a guesstimate
        traces_sample_rate=0.01,
        # truncate large requests @ 10kb
        request_bodies="medium",
        default_integrations=False,  # disable logging integration
        integrations=[
            AioHttpIntegration(),
            # all default integrations apart from logging
            ArgvIntegration(),
            AtexitIntegration(),
            DedupeIntegration(),
            ExcepthookIntegration(),
            ModulesIntegration(),
            StdlibIntegration(),
            ThreadingIntegration(),
        ],
    )
