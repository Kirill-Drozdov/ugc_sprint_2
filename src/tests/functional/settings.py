"""Пакет функциональными тестами проекта."""

from pydantic_settings import BaseSettings


class TestSettings(BaseSettings):
    postgres_user: str = 'postgres'
    postgres_password: str = 'postgres'
    postgres_db: str = 'postgres'
    postgres_host: str = 'localhost'
    pgport: int = 5432
    # Настройки Redis.
    redis_host: str = 'localhost'
    redis_port: int = 6379
    # Общие настройки проекта.
    app_port: int = 8888
    app_host: str = 'auth_api_test'
    project_name: str = 'auth'
    app_version: str = 'v0.0.1'
    authjwt_secret_key: str = 'authjwt_secret_key'
    jwt_access_expires_minutes: int = 15
    jwt_refresh_expires_days: int = 7


test_settings = TestSettings()
