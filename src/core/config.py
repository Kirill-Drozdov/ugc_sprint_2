from logging import config as logging_config
import os

from async_fastapi_jwt_auth import AuthJWT
from pydantic_settings import BaseSettings, SettingsConfigDict

from core.logger import LOGGING

# Применяем настройки логирования.
logging_config.dictConfig(LOGGING)

# Корень проекта.
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Settings(BaseSettings):
    """Настройки проекта."""
    # Настройки Postgres.
    postgres_user: str = 'postgres'
    postgres_password: str = 'postgres'
    postgres_db: str = 'postgres'
    postgres_host: str = 'localhost'
    pgport: int = 5432
    echo_mode: bool = False
    # Настройки Redis.
    redis_host: str = 'localhost'
    redis_port: int = 6379
    # Общие настройки проекта.
    app_port: int = 8000
    project_name: str = 'auth'
    app_version: str = 'v0.0.1'
    authjwt_secret_key: str = 'authjwt_secret_key'
    jwt_access_expires_minutes: int = 15
    jwt_refresh_expires_days: int = 7
    jaeger_host_name: str = 'jaeger'
    jaeger_port: int = 6831
    yandex_oauth_client_id: str = 'secret'
    yandex_oauth_client_secret: str = 'secret'
    yandex_oauth_redirect_uri: str = 'http://localhost:8000/api/v1/auth/yandex/callback'
    trace_mode: bool = False
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        extra='ignore',
    )


settings = Settings()


@AuthJWT.load_config
def get_config():
    return Settings()
