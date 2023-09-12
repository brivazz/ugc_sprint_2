# Из-за того, что mypy ругается на
# error: Class cannot subclass "BaseSettings" (has type "Any")  [misc]
# из-за новой версии pydantic v2, игнор всего файла

# mypy: ignore-errors
"""Модуль Конфигурации тестов для приложения UGC2."""

from pathlib import Path

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    """Класс, представляющий настройки приложения."""

    ugc2_api_project_name: str = Field('movies')
    sentry_dsn: str = Field('https://sentry.io')
    debug: str = Field('False')
    base_dir: Path = Path(__file__).resolve().parent.parent  # tests/

    service_url: str = Field('http://127.0.0.1:8000')
    auth_url: str = Field('http://nginx/api/v1/auth')

    mongo_db: str = Field('ugc2_movies')
    mongo_host: str = Field('localhost')
    mongo_port: int = Field(27017)


settings_test = Settings()
