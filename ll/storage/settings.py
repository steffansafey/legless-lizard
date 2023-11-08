import os

from pydantic import Field
from pydantic_settings import BaseSettings


class PostgresSettings(BaseSettings):
    DATABASE: str = Field(alias="POSTGRES_DB")
    USER: str = Field(alias="POSTGRES_USER")
    PASSWORD: str = Field(alias="POSTGRES_PASSWORD")
    HOST: str = Field(alias="POSTGRES_HOST")
    PORT: int = Field(alias="POSTGRES_PORT")

    @property
    def configuration_dict(self) -> dict:
        """Return a dictionary containing the configuration for the Postgres db."""
        test = "test_" if os.environ.get("TEST") else ""
        return {
            "database": test + self.DATABASE,
            "user": self.USER,
            "password": self.PASSWORD,
            "host": self.HOST,
            "port": self.PORT,
        }

    @property
    def connection_string(self):
        """Format a connection string from Postgres settings."""
        return "postgresql://{user}:{password}@{host}:{port}/{database}".format(
            **self.configuration_dict
        )
