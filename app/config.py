"""Settings read from the environment (and from .env during local development)."""

from functools import lru_cache

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import URL

from app import constants


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=constants.ENV_FILE,
        extra="ignore",
    )

    db_host: str = constants.DEFAULT_DB_HOST
    db_port: int = constants.DEFAULT_DB_PORT
    db_name: str
    db_user: str
    db_password: SecretStr

    campaign_name_prefix: str

    keitaro_url: str
    keitaro_api_key: SecretStr
    keitaro_domain_id: int
    keitaro_group_id: int
    keitaro_traffic_source_id: int

    @property
    def database_url(self) -> URL:
        return URL.create(
            drivername=constants.DB_DRIVER,
            username=self.db_user,
            password=self.db_password.get_secret_value(),
            host=self.db_host,
            port=self.db_port,
            database=self.db_name,
            query={"charset": constants.DB_CHARSET},
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]