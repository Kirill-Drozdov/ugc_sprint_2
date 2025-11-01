from logging import config as logging_config
import os

from pydantic_settings import BaseSettings, SettingsConfigDict

from core.logger import LOGGING

# Применяем настройки логирования.
logging_config.dictConfig(LOGGING)

# Корень проекта.
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Settings(BaseSettings):
    """Настройки проекта."""
    # Общие настройки проекта.
    app_port: int = 8000
    project_name: str = 'UGC API 2'
    app_version: str = 'v0.0.1'
    # Подключение к MongoDB.
    mongo_host: str = 'localhost'
    mongo_port: int = 27019

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        extra='ignore',
    )


settings = Settings()
