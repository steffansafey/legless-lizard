from pydantic import Field
from pydantic_settings import BaseSettings

from ll.sentry import SentrySettings
from ll.settings import LogLevel
from ll.storage.settings import PostgresSettings


class Settings(BaseSettings):
    DEBUG: bool = Field(default=False, alias="DEBUG")
    LOG_LEVEL: LogLevel = Field(default=LogLevel.INFO, alias="LOG_LEVEL")
    BUILD_VERSION: str = Field(default="dev", alias="BUILD_VERSION")
    API_DOCS: bool = Field(default=False, alias="API_DOCS")
    SENTRY: SentrySettings = SentrySettings()
    POSTGRES: PostgresSettings = PostgresSettings()
