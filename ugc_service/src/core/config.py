# Из-за того, что mypy ругается на
# error: Class cannot subclass "BaseSettings" (has type "Any")  [misc]
# из-за новой версии pydantic v2, игнор всего файла

# mypy: ignore-errors
"""Модуль Конфигурации приложения UGC."""

from pathlib import Path

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    """Класс, представляющий настройки приложения."""

    project_name: str = Field('movies', env='UGC_2_PROJECT_NAME')
    debug: str = Field('False', env='DEBUG')
    sentry_dsn: str = Field('https://sentry.io', env='SENTRY_DSN')
    sentry_traces_sample_rate: float = Field(1.0, env='SENTRY_TRACES_SAMPLE_RATE')
    base_dir: Path = Path(__file__).resolve().parent.parent
    auth_server_url: str = Field('http://nginx/api/v1/auth', env='AUTH_URL')

    mongo_db: str = Field('ugc2_movies', env='MONGO_DB')
    mongo_username: str = Field('root', env='MONGO_LOGIN')
    mongo_password: str = Field('example', env='MONGO_PASSWORD')
    mongo_host: str = Field('localhost', env='MONGO_HOST')
    mongo_port: int = Field(27017, env='MONGO_PORT')


settings = Settings()
